
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
        """Define the model fields exposed through the API."""

        model = Job

        fields = [
            'job_id',
            'employer_id',
            'job_title',
            'description',
            'responsibilities',
            'qualifications',
            'benefits',
            'skills',
            'min_experience',
            'max_experience',
            'salary_min',
            'salary_max',
            'salary_currency',
            'salary_period',
            'salary',
            'location',
            'employment_type',
            'work_mode',
            'vacancies',
            'application_deadline',
            'status',
            'published_at',
            'is_active',
            'is_deleted',
            'deleted_at',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'job_id',
            'employer_id',
            'status',
            'is_active',
            'published_at',
            'is_deleted',
            'deleted_at',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        """
        Validate experience and salary ranges.
        """

        instance = self.instance

        min_experience = attrs.get(
            'min_experience',
            instance.min_experience if instance else 0
        )

        max_experience = attrs.get(
            'max_experience',
            instance.max_experience if instance else None
        )

        salary_min = attrs.get(
            'salary_min',
            instance.salary_min if instance else None
        )

        salary_max = attrs.get(
            'salary_max',
            instance.salary_max if instance else None
        )

        if (
            max_experience is not None
            and min_experience > max_experience
        ):
            raise serializers.ValidationError({
                'max_experience': (
                    'Maximum experience must be greater than '
                    'or equal to minimum experience.'
                )
            })

        if (
            salary_min is not None
            and salary_max is not None
            and salary_min > salary_max
        ):
            raise serializers.ValidationError({
                'salary_max': (
                    'Maximum salary must be greater than '
                    'or equal to minimum salary.'
                )
            })

        return attrs
