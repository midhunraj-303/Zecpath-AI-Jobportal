
from django.db import models

from apps.candidates.models import Candidate
from apps.jobs.models import Job


class ApplicationStatus(models.TextChoices):
    """Define the possible statuses of a job application."""

    PENDING = 'PENDING', 'Pending'
    REVIEWING = 'REVIEWING', 'Reviewing'
    SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
    REJECTED = 'REJECTED', 'Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'


class Application(models.Model):
    """Store a candidate's application for a particular job."""

    application_id = models.BigAutoField(primary_key=True)

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.PROTECT,
        related_name='applications'
    )

    resume = models.FileField(
        upload_to='applications/resume/',
        blank=True,
        null=True
    )

    cover_letter = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Define database-level constraints for applications."""

        constraints = [
            models.UniqueConstraint(
                fields=['candidate', 'job'],
                name='unique_candidate_job_application'
            )
        ]

    def __str__(self):
        """Return a readable representation of the application."""

        return (
            f'{self.candidate.full_name} - '
            f'{self.job.job_title}'
        )
