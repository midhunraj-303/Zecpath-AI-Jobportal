
from django.conf import settings
from django.db import models
from django.utils import timezone


class ActiveProfileManager(models.Manager):
    """Return only profiles that have not been soft-deleted."""

    def get_queryset(self):
        """Build a queryset containing active profiles only.

        Returns:
            QuerySet: Profiles where is_deleted is False.
        """
        return super().get_queryset().filter(is_deleted=False)



class Candidate(models.Model):
    """Store professional profile information for a candidate."""

    candidate_id = models.BigAutoField(primary_key=True)

    objects = models.Manager()
    active_objects = ActiveProfileManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )

    # Personal and professional information
    full_name = models.CharField(max_length=200)
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True
    )
    skills = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    expected_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Profile lifecycle management
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def soft_delete(self):
        """Mark the candidate profile as deleted without removing its data."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a previously soft-deleted candidate profile."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def __str__(self):
        """Return the candidate's full name."""
        return self.full_name



class Education(models.Model):
    """Store an individual educational qualification for a candidate."""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='educations'
    )

    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150, blank=True)
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )
    grade = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the qualification and institution."""
        return f'{self.degree} - {self.institution}'



class Experience(models.Model):
    """Store an individual employment record for a candidate."""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='experiences'
    )

    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=150)
    employment_type = models.CharField(
        max_length=50,
        blank=True
    )
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True
    )
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the job title and company name."""
        return f'{self.job_title} - {self.company_name}'





