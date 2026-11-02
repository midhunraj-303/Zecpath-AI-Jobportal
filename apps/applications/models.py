from django.db import models
from apps.candidates.models import Candidate
from apps.jobs.models import Job

# Create your models here.

class ApplicationStatus(models.TextChoices):
    PENDING = 'PENDING','Pending'
    REVIEWING = 'REVIEWING', 'Reviewing'
    SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
    REJECTED = 'REJECTED','Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'

class Application(models.Model):

    # Primary Key
    application_id = models.BigAutoField(
        primary_key=True
    )

    #Relationship with Candidate
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    # Relationship with Job
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    # Application Information
    resume = models.FileField(
        upload_to='applications/resume/',
        blank = True,
        null = True
    )

    cover_letter = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )

    # Timestamps
    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        # A candidate can apply only once for a particular job
        constraints = [
            models.UniqueConstraint(
                fields=['candidate','job'],
                name='unique_candidate_job_application'
            )
        ]

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.job_title}"

    
