
from rest_framework import serializers

from apps.candidates.serializers import ResumeUploadSerializer

from .models import (
    Application, 
    ApplicationStatus,
    ApplicationStatusHistory,
    ApplicationNotification
)

class ApplicationSerializer(serializers.ModelSerializer):
    """Serialize application data for API requests and responses."""

    candidate_id = serializers.IntegerField(
        source='candidate.candidate_id',
        read_only=True
    )

    candidate_name = serializers.CharField(
        source='candidate.full_name',
        read_only=True
    )

    job_id = serializers.IntegerField(
        source='job.job_id',
        read_only=True
    )

    job_title = serializers.CharField(
        source='job.job_title',
        read_only=True
    )

    resume = serializers.FileField(
        write_only=True, # does not return the file or its URL in the response
        required=False, # two choices
        allow_null=True
    )

    company_name = serializers.CharField(
        source='job.employer.company_name',
        read_only=True
    )

    resume_name = serializers.SerializerMethodField()

    class Meta:
        """Define the fields exposed by the Application API."""

        model = Application

        fields = [
            'application_id',
            'candidate_id',
            'candidate_name',
            'job_id',
            'job_title',
            'company_name',
            'resume',
            'resume_name',
            'cover_letter',
            'status',
            'applied_at',
            'updated_at'
        ]

        read_only_fields = [
            'application_id',
            'candidate_id',
            'job_id',
            'job_title',
            'resume_name',
            'status',
            'applied_at',
            'updated_at'
        ]

    def validate_resume(self, uploaded_file):
        """Validate an application-specific resume.

        Args:
            uploaded_file: The uploaded resume file.

        Returns:
            UploadedFile: The validated resume file.

        Raises:
            serializers.ValidationError: If the resume is invalid.
        """
        if uploaded_file is None:
            return uploaded_file

        validator = ResumeUploadSerializer(
            data={'resume': uploaded_file}
        )

        validator.is_valid(raise_exception=True)

        return validator.validated_data['resume']

    def get_resume_name(self, obj):
        """Return the resume filename without exposing its URL.

        Args:
            obj: Application model instance.

        Returns:
            str or None: The stored resume filename.
        """
        if not obj.resume:
            return None

        return obj.resume.name.rsplit('/', 1)[-1]



class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Validate application status updates.

    Enforce permitted status transitions before saving an application.
    """

    status = serializers.ChoiceField(
        choices=ApplicationStatus.choices,
        required=True
    )

    class Meta:
        """Define the fields allowed for status updates."""

        model = Application
        fields = ['status']

    def validate_status(self, new_status):
        """
        Validate whether the requested status transition is permitted.

        Args:
            new_status: The status requested by the employer.

        Returns:
            str: The validated application status.

        Raises:
            serializers.ValidationError: If the transition is invalid.
        """

        application = self.instance
        current_status = application.status

        allowed_transitions = {
            ApplicationStatus.APPLIED: [
                ApplicationStatus.REVIEWING,
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.REJECTED,
            ],
            ApplicationStatus.REVIEWING: [
                ApplicationStatus.SHORTLISTED,
                ApplicationStatus.INTERVIEW_SCHEDULED,
                ApplicationStatus.REJECTED,
            ],
            ApplicationStatus.SHORTLISTED: [
                ApplicationStatus.INTERVIEW_SCHEDULED,
                ApplicationStatus.REJECTED,
            ],
            ApplicationStatus.INTERVIEW_SCHEDULED: [
                ApplicationStatus.SELECTED,
                ApplicationStatus.REJECTED,
            ],
            ApplicationStatus.SELECTED: [],
            ApplicationStatus.REJECTED: [],
        }

        # Allow the current status without creating a new history record.
        if new_status == current_status:
            return new_status

        permitted_statuses = allowed_transitions.get(
            current_status,
            []
        )

        if new_status not in permitted_statuses:
            raise serializers.ValidationError(
                f"Cannot change application status from "
                f"{current_status} to {new_status}."
            )

        return new_status



class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serialize application status history for API responses.

    Exposes the previous status, new status, user responsible
    for the change, remarks, and timestamp.
    """

    changed_by_username = serializers.CharField(
        source='changed_by.username',
        read_only=True,
        default=None
    )

    class Meta:
        """Define the fields exposed by the history API."""

        model = ApplicationStatusHistory

        fields = [
            'history_id',
            'previous_status',
            'new_status',
            'changed_by_username',
            'remarks',
            'changed_at'
        ]

        read_only_fields = fields



class ApplicationTrackingSerializer(serializers.ModelSerializer):
    """
    Serialize application details along with its status timeline.
    """

    job_title = serializers.CharField(
        source='job.job_title',
        read_only=True
    )

    company_name = serializers.CharField(
        source='job.employer.company_name',
        read_only=True
    )

    current_status = serializers.CharField(
        source='status',
        read_only=True
    )

    history_available = serializers.SerializerMethodField()

    timeline = ApplicationStatusHistorySerializer(
        source='status_history',
        many=True,
        read_only=True
    )

    class Meta:
        model = Application

        fields = [
            'application_id',
            'job_title',
            'company_name',
            'current_status',
            'applied_at',
            'history_available',
            'timeline'
        ]

        read_only_fields = fields

    def get_history_available(self, obj):
        """Check whether status history exists for this application."""

        return obj.status_history.exists()


class ApplicationNotificationSerializer(serializers.ModelSerializer):
    """
    Serialize application notifications for candidate API responses.
    """

    application_id = serializers.IntegerField(
        source='application.application_id',
        read_only=True
    )

    job_title = serializers.CharField(
        source='application.job.job_title',
        read_only=True
    )

    class Meta:
        """Define the fields exposed by the notification API."""

        model = ApplicationNotification

        fields = [
            'notification_id',
            'application_id',
            'job_title',
            'title',
            'message',
            'is_read',
            'created_at'
        ]

        read_only_fields = fields