
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

from django.db.models import Count
from apps.applications.models import Application,ApplicationStatus

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



class EmployerApplicationStatsAPIView(APIView):
    """
    Provide application statistics for the authenticated employer.
    """

    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request):
        """
        Retrieve application counts grouped by ATS status.

        Returns:
            Response: Total applications and status-wise counts.
        """

        employer = get_object_or_404(
            Employer.active_objects,
            user=request.user
        )

        # Retrieve applications for this employer's jobs only.
        applications = Application.objects.filter(
            job__employer=employer
        )

        # Count applications grouped by status.
        status_counts = applications.values(
            'status'
        ).annotate(
            total=Count('application_id')
        )

        # Initialize all statuses with zero.
        counts = {
            application_status: 0
            for application_status, _ in ApplicationStatus.choices
        }

        # Update counts from the database.
        for item in status_counts:
            counts[item['status']] = item['total']


       #Shortlist ration 
        total_applications = applications.count()

        shortlisted_count = counts['SHORTLISTED']
        rejected_count = counts['REJECTED']
        selection_count = counts['SELECTED']

        shortlist_ratio = (
            round((shortlisted_count / total_applications) * 100, 2)
            if total_applications > 0
            else 0.0
        )

        return Response(
            {
                'total_applications': applications.count(),
                'shortlist_ratio': shortlist_ratio,
                'status_counts': counts,
                
            },
            status=status.HTTP_200_OK
        )
