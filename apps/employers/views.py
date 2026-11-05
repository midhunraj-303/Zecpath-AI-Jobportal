
"""
Views for employer profile management.
"""

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsEmployer
from .models import Employer
from .serializers import EmployerSerializer


class EmployerProfileAPIView(APIView):
    """
    Create, retrieve, update and soft-delete employer profiles.
    """

    permission_classes = [IsAuthenticated, IsEmployer]

    def get_object(self, user):
        """
        Retrieve the active employer profile belonging to a user.

        Args:
            user: The authenticated employer user.

        Returns:
            Employer: The employer profile.

        Raises:
            Http404: If no active profile exists.
        """
        return get_object_or_404(
            Employer.active_objects,
            user=user
        )

    def post(self, request):
        """
        Create an employer profile if one does not already exist.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Existing or newly created employer profile.
        """
        existing_profile = Employer.objects.filter(
            user=request.user
        ).first()

        if existing_profile:
            if existing_profile.is_deleted:
                return Response(
                    {
                        'error': (
                            'Your profile is deleted. '
                            'Contact an admin for restoration.'
                        )
                    },
                    status=status.HTTP_409_CONFLICT
                )

            serializer = EmployerSerializer(existing_profile)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        serializer = EmployerSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        """
        Retrieve the authenticated employer's active profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Employer profile information.
        """
        employer = self.get_object(request.user)
        serializer = EmployerSerializer(employer)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        """
        Completely update the employer's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Updated profile or validation errors.
        """
        employer = self.get_object(request.user)

        serializer = EmployerSerializer(
            employer,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        """
        Partially update the employer's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Updated profile or validation errors.
        """
        employer = self.get_object(request.user)

        serializer = EmployerSerializer(
            employer,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        """
        Soft-delete the authenticated employer's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Confirmation of profile deletion.
        """
        employer = self.get_object(request.user)
        employer.soft_delete()

        return Response(
            {
                'message': 'Employer profile deleted successfully.'
            },
            status=status.HTTP_200_OK
        )
