"""
Serializers for employer-related API operations.
"""

from rest_framework import serializers
from .models import Employer

class EmployerSerializer(serializers.ModelSerializer):
    """
    Serialize employer profile information.

    The associated user is assigned by the authenticated request,
    not supplied directly by the API client
    """

    employer_id = serializers.IntegerField(read_only = True)

    class Meta:
        """
        Define the model and fields exposed by the serializer
        """

        model = Employer

        fields = [
            'employer_id',
            'company_name',
            'company_description',
            'website',
            'location',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'employer_id',
            'created_at',
            'updated_at',
        ]

        