
"""
Serializers for job-related API operations.
"""

from rest_framework import serializers

from .models import Job,Skill


class JobSerializer(serializers.ModelSerializer):
    """
    Serialize job information for API requests and responses.

    The employer is assigned from the authenticated user.
    """

    employer_id = serializers.IntegerField(
        source='employer.employer_id',
        read_only=True
    )

    # Connect approved skills to job creation
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(
            approval_status=Skill.ApprovalStatus.APPROVED,
            is_active=True
        ),
        many=True,
        required=False
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




# Employers can submit only skill_name.
# Employers cannot choose their own approval status.
# Duplicate names are rejected, even with different letter casing.
class SkillSerializer(serializers.ModelSerializer):
    """
    Serialize skills for listing and employer skill suggestions.
    """

    class Meta:
        """Define the fields exposed through the skill API."""

        model = Skill

        fields = [
            'skill_id',
            'skill_name',
            'approval_status',
            'created_at',
        ]

        read_only_fields = [
            'skill_id',
            'approval_status',
            'created_at',
        ]

    def validate_skill_name(self, value):
        """
        Validate and normalize a skill name.

        Prevent duplicate skill names regardless of letter case.
        """

        value = ' '.join(value.split())

        if not value:
            raise serializers.ValidationError(
                'Skill name cannot be empty.'
            )

        normalized_name = value.casefold()

        existing_skill = Skill.objects.filter(
            normalized_name=normalized_name
        )

        if self.instance:
            existing_skill = existing_skill.exclude(
                skill_id=self.instance.skill_id
            )

        if existing_skill.exists():
            raise serializers.ValidationError(
                'This skill already exists.'
            )

        return value
