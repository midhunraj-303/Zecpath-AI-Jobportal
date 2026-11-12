
"""
Models for job management and skill classification.
"""

from django.db import models
from django.db.models import F, Q

from apps.employers.models import Employer
from django.conf import settings 


def migrate_existing_job_data(apps, schema_editor):
    """
    Migrate existing job records to the new schema.

    Preserve existing salary amounts and map the legacy active
    flag to the new job lifecycle status.
    """

    Job = apps.get_model('jobs', 'Job')

    # Copy the existing salary into both range boundaries.
    # Leave currency and salary period unspecified.
    Job.objects.filter(salary__isnull=False).update(
        salary_min=models.F('salary'),
        salary_max=models.F('salary')
    )

    # Map existing active jobs to PUBLISHED.
    Job.objects.filter(is_active=True).update(
        status='PUBLISHED'
    )

    # Map existing inactive jobs to PAUSED.
    Job.objects.filter(is_active=False).update(
        status='PAUSED'
    )

class EmploymentType(models.TextChoices):
    """Available employment arrangements."""

    FULL_TIME = 'FULL_TIME', 'Full Time'
    PART_TIME = 'PART_TIME', 'Part Time'
    CONTRACT = 'CONTRACT', 'Contract'
    INTERNSHIP = 'INTERNSHIP', 'Internship'
    TEMPORARY = 'TEMPORARY', 'Temporary'
    FREELANCE = 'FREELANCE', 'Freelance'


class WorkMode(models.TextChoices):
    """Available workplace arrangements."""

    ONSITE = 'ONSITE', 'On-site'
    REMOTE = 'REMOTE', 'Remote'
    HYBRID = 'HYBRID', 'Hybrid'


class SalaryPeriod(models.TextChoices):
    """Salary payment periods."""

    YEAR = 'YEAR', 'Per Year'
    MONTH = 'MONTH', 'Per Month'
    HOUR = 'HOUR', 'Per Hour'


class JobStatus(models.TextChoices):
    """Lifecycle states of a job posting."""

    DRAFT = 'DRAFT', 'Draft'
    PUBLISHED = 'PUBLISHED', 'Published'
    PAUSED = 'PAUSED', 'Paused'
    CLOSED = 'CLOSED', 'Closed'
    EXPIRED = 'EXPIRED', 'Expired'



class Skill(models.Model):
    """Represent a reusable skill in the job portal."""

    class ApprovalStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    skill_id = models.BigAutoField(primary_key=True)

    skill_name = models.CharField(
        max_length=100,
        unique=True
    )

    # Prevents case-insensitive duplicates
    normalized_name = models.CharField(
        max_length=100,
        unique=True,
        editable=False
    )

    # Tracks pending, approved and rejected skills
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING
    )

    # Allows administrators to deactivate skills
    is_active = models.BooleanField(default=True)

    # Identifies the employer who suggested a skill
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_skills'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Normalize the skill name before saving."""

        self.skill_name = ' '.join(self.skill_name.split())
        self.normalized_name = self.skill_name.casefold()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return the skill name."""

        return self.skill_name



class Job(models.Model):
    """Represent a job posting created by an employer."""

    job_id = models.BigAutoField(primary_key=True)

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    job_title = models.CharField(max_length=200)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    benefits = models.TextField(blank=True)

    skills = models.ManyToManyField(
        Skill,
        related_name='jobs',
        blank=True
    )

    min_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )
    max_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True
    )

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    salary_currency = models.CharField(
        max_length=3,
        blank=True,
        null=True
    )
    salary_period = models.CharField(
        max_length=10,
        choices=SalaryPeriod.choices,
        blank=True,
        null=True
    )

    # Legacy field retained during the API transition.
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    location = models.CharField(max_length=200)

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )

    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.ONSITE
    )

    vacancies = models.PositiveIntegerField(default=1)

    application_deadline = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.DRAFT
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True
    )

    is_featured = models.BooleanField(      # is_featured: Whether the job is promoted as a featured job.
        default=False,
        db_index=True
    )

    featured_until = models.DateField(      # featured_until: The last date the job should appear as featured.
        blank=True,
        null=True                           # featured_until=None: No scheduled expiry date.
    )

    # Retained temporarily for backward compatibility.
    is_active = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta:
        """Define database constraints and query indexes."""

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(max_experience__isnull=True)
                    | Q(min_experience__lte=F('max_experience'))
                ),
                name='job_experience_range_valid'
            ),
            models.CheckConstraint(
                condition=(
                    Q(salary_min__isnull=True)
                    | Q(salary_max__isnull=True)
                    | Q(salary_min__lte=F('salary_max'))
                ),
                name='job_salary_range_valid'
            ),
        ]

        indexes = [
            models.Index(
                fields=['status', 'is_deleted', '-published_at'],
                name='job_public_listing_idx'
            ),
            models.Index(
                fields=['status', 'is_deleted', '-created_at'],
                name='job_latest_listing_idx'
            ),
            models.Index(
                fields=['location'],
                name='job_location_idx'
            ),
            models.Index(
                fields=['employment_type', 'work_mode'],
                name='job_type_mode_idx'
            ),
            models.Index(
                fields=['is_featured', 'featured_until'],
                name='job_featured_idx'
            ),
        ]

    def __str__(self):
        """Return the job title."""
        return self.job_title
