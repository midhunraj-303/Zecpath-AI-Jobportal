
from rest_framework import serializers

from .models import Candidate, Education, Experience


class EducationSerializer(serializers.ModelSerializer):
    """Serialize and validate a candidate's education record."""

    class Meta:
        """Define the education fields exposed through the API."""

        model = Education

        fields = [
            'id',
            'institution',
            'degree',
            'field_of_study',
            'start_year',
            'end_year',
            'grade',
        ]

        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate the education year range.

        Args:
            attrs: Validated education data.

        Returns:
            dict: Validated education data.

        Raises:
            serializers.ValidationError: If the year range is invalid.
        """
        start_year = attrs.get(
            'start_year',
            getattr(self.instance, 'start_year', None)
        )
        end_year = attrs.get(
            'end_year',
            getattr(self.instance, 'end_year', None)
        )

        if end_year and start_year and end_year < start_year:
            raise serializers.ValidationError(
                'End year cannot be earlier than start year.'
            )

        return attrs


class ExperienceSerializer(serializers.ModelSerializer):
    """Serialize and validate a candidate's work experience."""

    class Meta:
        """Define the experience fields exposed through the API."""

        model = Experience

        fields = [
            'id',
            'company_name',
            'job_title',
            'employment_type',
            'location',
            'start_date',
            'end_date',
            'is_current',
            'description',
        ]

        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate the employment date range.

        Args:
            attrs: Validated experience data.

        Returns:
            dict: Validated experience data.

        Raises:
            serializers.ValidationError: If the dates are inconsistent.
        """
        start_date = attrs.get(
            'start_date',
            getattr(self.instance, 'start_date', None)
        )
        end_date = attrs.get(
            'end_date',
            getattr(self.instance, 'end_date', None)
        )
        is_current = attrs.get(
            'is_current',
            getattr(self.instance, 'is_current', False)
        )

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                'End date cannot be earlier than start date.'
            )

        if is_current and end_date:
            raise serializers.ValidationError(
                'Current employment should not have an end date.'
            )

        return attrs


class CandidateProfileSerializer(serializers.ModelSerializer):
    """Serialize and validate candidate profile information."""

    educations = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)

    class Meta:
        """Define the fields exposed by the candidate profile API."""

        model = Candidate

        fields = [
            'candidate_id',
            'full_name',
            'resume',
            'skills',
            'location',
            'expected_salary',
            'educations',
            'experiences',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'candidate_id',
            'educations',
            'experiences',
            'created_at',
            'updated_at',
        ]

    def validate_full_name(self, value):
        """Reject candidate names containing only whitespace.

        Args:
            value: Submitted candidate name.

        Returns:
            str: Normalized candidate name.

        Raises:
            serializers.ValidationError: If the name is empty.
        """
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Full name cannot be empty.'
            )

        return value

    def validate_expected_salary(self, value):
        """Ensure the expected salary is positive.

        Args:
            value: Submitted expected salary.

        Returns:
            Decimal: Validated expected salary.

        Raises:
            serializers.ValidationError: If salary is not positive.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Expected salary must be greater than zero.'
            )

        return value
