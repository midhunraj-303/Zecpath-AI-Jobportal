
"""
Serializers for job-related API operations.
"""

from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    """
    Serialize job information for API requests and responses.

    The employer is assigned from the authenticated user.
    """

    employer_id = serializers.IntegerField(
        source='employer.employer_id',
        read_only=True
    )

    class Meta:
        """Define the model and fields exposed by the serializer."""

        model = Job

        fields = [
            'job_id',
            'employer_id',
            'job_title',
            'description',
            'location',
            'salary',
            'employment_type',
            'work_mode',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'job_id',
            'employer_id',
            'created_at',
            'updated_at',
        ]
