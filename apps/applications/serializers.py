
from rest_framework import serializers

from .models import Application,ApplicationStatus


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

    class Meta:
        """Define the fields exposed by the Application API."""

        model = Application

        fields = [
            'application_id',
            'candidate_id',
            'job_id',
            'job_title',
            'resume',
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
            'status',
            'applied_at',
            'updated_at'
        ]





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
