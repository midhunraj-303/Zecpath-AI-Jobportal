
from django.db import models

from apps.candidates.models import Candidate
from apps.jobs.models import Job


class ApplicationStatus(models.TextChoices):
    """Define the possible statuses of a job application."""

    APPLIED = 'APPLIED', 'Applied'
    REVIEWING = 'REVIEWING', 'Reviewing'
    SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
    INTERVIEW_SCHEDULED = (
        'INTERVIEW_SCHEDULED',
        'Interview Scheduled'
    )
    REJECTED = 'REJECTED', 'Rejected'
    SELECTED = 'SELECTED', 'Selected'

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
        default=ApplicationStatus.APPLIED
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
            f'Application {self.application.application_id}: '
            f'{previous} -> {self.new_status}'
        )


class ApplicationNotification(models.Model):
    """
    Store application-related notifications for candidates.

    Each notification informs a candidate about an update
    to one of their job applications.
    """

    notification_id = models.BigAutoField(primary_key=True)

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(max_length=150)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Define notification ordering and database indexes."""

        ordering = ['-created_at']

        indexes = [
            models.Index(
                fields=['candidate', 'is_read', '-created_at'],
                name='candidate_notification_idx'
            )
        ]

        verbose_name = 'Application Notification'
        verbose_name_plural = 'Application Notifications'

    def __str__(self):
        """Return a readable notification description."""

        return (
            f'{self.title} - '
            f'{self.candidate.full_name}'
        )