
"""
Serializers for employer-related API operations.
"""

from rest_framework import serializers

from .models import Employer


class EmployerSerializer(serializers.ModelSerializer):
    """
    Serialize and validate employer profile information.

    The associated user and verification status are controlled
    by the backend and cannot be modified by employers.
    """

    employer_id = serializers.IntegerField(read_only=True)

    class Meta:
        """Define the model and fields exposed by the serializer."""

        model = Employer

        fields = [
            'employer_id',
            'company_name',
            'company_domain',
            'company_size',
            'company_description',
            'website',
            'location',
            'is_verified',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'employer_id',
            'is_verified',
            'created_at',
            'updated_at',
        ]

    def validate_company_name(self, value):
        """
        Ensure the company name is not empty.

        Args:
            value: Submitted company name.

        Returns:
            str: Normalized company name.

        Raises:
            serializers.ValidationError: If the name is empty.
        """
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Company name cannot be empty.'
            )

        return value
