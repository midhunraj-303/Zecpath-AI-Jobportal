
from rest_framework import serializers

from apps.candidates.serializers import ResumeUploadSerializer

from .models import (
    Application, 
    ApplicationStatus,
    ApplicationStatusHistory
)

class ApplicationSerializer(serializers.ModelSerializer):
    """Serialize application data for API requests and responses."""

    candidate_id = serializers.IntegerField(
        source='candidate.candidate_id',
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

    resume_name = serializers.SerializerMethodField()

    class Meta:
        """Define the fields exposed by the Application API."""

        model = Application

        fields = [
            'application_id',
            'candidate_id',
            'job_id',
            'job_title',
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
    """Validate and update an application's status."""

    status = serializers.ChoiceField(
        choices=ApplicationStatus.choices,
        required=True
    )

    class Meta:
        """Define the fields allowed for status updates."""

        model = Application
        fields = ['status']




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
