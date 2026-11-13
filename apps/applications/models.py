
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



class ApplicationStatusHistory(models.Model):
    """
    Maintain an audit trail of application status changes.

    Each record represents one status transition, including the
    initial application submission.
    """

    history_id = models.BigAutoField(
        primary_key=True,
        help_text="Unique identifier for the status history record."
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text="Application associated with this status change."
    )

    previous_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        blank=True,
        null=True,
        help_text="Status before the transition; null for initial submission."
    )

    new_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        help_text="New status assigned to the application."
    )

    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_status_changes',
        help_text="User responsible for the status change."
    )

    remarks = models.TextField(
        blank=True,
        help_text="Optional explanation for the status change."
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the status change was recorded."
    )

    class Meta:
        """Define default ordering and database indexes."""

        ordering = ['changed_at']

        indexes = [
            models.Index(
                fields=['application', 'changed_at'],
                name='app_status_history_idx'
            )
        ]

        verbose_name = "Application Status History"
        verbose_name_plural = "Application Status Histories"

    def __str__(self):
        """Return a readable description of the status transition."""

        previous = self.previous_status or "INITIAL"

        return (
            f'Application {self.application_id}: '
            f'{previous} -> {self.new_status}'
        )
