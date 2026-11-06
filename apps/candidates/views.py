
"""
Views for candidate profile management.
"""

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsCandidate

from .models import Candidate
from .serializers import (
    CandidateProfileSerializer,
    ResumeUploadSerializer
)
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser


class CandidateProfileAPIView(APIView):
    """
    Create, retrieve, update and soft-delete candidate profiles.
    """

    permission_classes = [IsAuthenticated, IsCandidate]

    def get_object(self, user):
        """
        Retrieve the active profile belonging to a candidate.

        Args:
            user: The authenticated candidate user.

        Returns:
            Candidate: The candidate's active profile.

        Raises:
            Http404: If no active candidate profile exists.
        """
        return get_object_or_404(
            Candidate.active_objects,
            user=user
        )

    def post(self, request):
        """
        Create a candidate profile if one does not already exist.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Existing or newly created candidate profile.
        """
        existing_profile = Candidate.objects.filter(
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

            serializer = CandidateProfileSerializer(
                existing_profile
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        serializer = CandidateProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        """
        Retrieve the authenticated candidate's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Candidate profile information.
        """
        candidate = self.get_object(request.user)

        serializer = CandidateProfileSerializer(candidate)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        """
        Completely update the candidate's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Updated candidate profile.
        """
        candidate = self.get_object(request.user)

        serializer = CandidateProfileSerializer(
            candidate,
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
        Partially update the candidate's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Updated candidate profile.
        """
        candidate = self.get_object(request.user)

        serializer = CandidateProfileSerializer(
            candidate,
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
        Soft-delete the authenticated candidate's profile.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Confirmation of profile deletion.
        """
        candidate = self.get_object(request.user)

        candidate.soft_delete()

        return Response(
            {
                'message': (
                    'Candidate profile deleted successfully.'
                )
            },
            status=status.HTTP_200_OK
        )



class ResumeAPIView(APIView):
    """Handle secure resume uploads for authenticated candidates."""

    permission_classes = [IsAuthenticated, IsCandidate]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Upload or replace the authenticated candidate's resume.

        Args:
            request: Multipart request containing the resume file.

        Returns:
            Response: Upload confirmation and file information.

        Raises:
            serializers.ValidationError: If resume validation fails.
            Http404: If the candidate profile does not exist.
        """
        candidate = get_object_or_404(
            Candidate.active_objects,
            user=request.user
        )

        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['resume']

        old_resume_name = (
            candidate.resume.name if candidate.resume else None
        )

        storage = candidate.resume.storage

        candidate.resume.save(
            uploaded_file.name,
            uploaded_file,
            save=False
        )

        new_resume_name = candidate.resume.name

        try:
            with transaction.atomic():
                candidate.save(
                    update_fields=['resume', 'updated_at']
                )

                if old_resume_name:
                    transaction.on_commit(
                        lambda: storage.delete(old_resume_name)
                    )

        except Exception:
            storage.delete(new_resume_name)
            raise

        return Response(
            {
                'message': 'Resume uploaded successfully.',
                'resume_name': candidate.resume.name.rsplit(
                    '/',
                    1
                )[-1],
                'file_size': uploaded_file.size,
            },
            status=status.HTTP_200_OK
            if old_resume_name
            else status.HTTP_201_CREATED
        )
