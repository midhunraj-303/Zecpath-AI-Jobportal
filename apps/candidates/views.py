
"""
Views for candidate profile management.
"""

from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status,generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsCandidate
from apps.jobs.models import Job

from .models import Candidate, SavedJob
from .serializers import (
    CandidateProfileSerializer,
    ResumeUploadSerializer,
    SavedJobSerializer,
    RecommendedJobSerializer,
)

from .services import get_recommended_jobs

from apps.applications.models import ApplicationNotification
from apps.applications.serializers import ApplicationNotificationSerializer


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
                        lambda: storage.delete(old_resume_name),
                        robust=True
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



class CandidateResumeDownloadAPIView(APIView):
    """Allow candidates to securely download their own resumes."""

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):
        """Download the authenticated candidate's resume.

        Args:
            request: The authenticated API request.

        Returns:
            FileResponse: The candidate's resume as an attachment.

        Raises:
            Http404: If the profile or resume does not exist.
        """
        candidate = get_object_or_404(
            Candidate.active_objects,
            user=request.user
        )

        if not candidate.resume:
            return Response(
                {'error': 'Resume not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not candidate.resume.storage.exists(
            candidate.resume.name
        ):
            return Response(
                {'error': 'Resume file is missing from storage.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            candidate.resume.open('rb'),
            as_attachment=True,
            filename=candidate.resume.name.rsplit('/', 1)[-1]
        )


class SavedJobsAPIView(APIView):
    """
    Retrieve and create saved jobs for authenticated candidates.
    """

    permission_classes = [IsAuthenticated, IsCandidate]

    def get_candidate(self, user):
        """
        Retrieve the authenticated candidate's active profile.

        Args:
            user: The authenticated candidate user.

        Returns:
            Candidate: The candidate's active profile.
        """
        return get_object_or_404(
            Candidate.active_objects,
            user=user
        )

    def get(self, request):
        """
        Retrieve all jobs saved by the authenticated candidate.

        Args:
            request: The authenticated API request.

        Returns:
            Response: List of saved jobs.
        """
        candidate = self.get_candidate(request.user)

        saved_jobs = SavedJob.objects.filter(
            candidate=candidate
        ).select_related(
            'job',
            'job__employer'
        )

        serializer = SavedJobSerializer(
            saved_jobs,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Save a published job for the authenticated candidate.

        Args:
            request: The authenticated API request.

        Returns:
            Response: Saved job details.
        """
        candidate = self.get_candidate(request.user)

        serializer = SavedJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = serializer.validated_data['job']

        available_job = Job.objects.filter(
            job_id=job.job_id,
            status='PUBLISHED',
            is_active=True,
            is_deleted=False
        ).filter(
            Q(application_deadline__isnull=True)
            | Q(application_deadline__gte=timezone.localdate())
        ).exists()

        if not available_job:
            return Response(
                {
                    'error': (
                        'This job is no longer available '
                        'for saving.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if SavedJob.objects.filter(
            candidate=candidate,
            job=job
        ).exists():
            return Response(
                {
                    'error': 'You have already saved this job.'
                },
                status=status.HTTP_409_CONFLICT
            )

        saved_job = serializer.save(candidate=candidate)

        return Response(
            SavedJobSerializer(saved_job).data,
            status=status.HTTP_201_CREATED
        )


class SavedJobDetailAPIView(APIView):
    """
    Remove a saved job belonging to the authenticated candidate.
    """

    permission_classes = [IsAuthenticated, IsCandidate]

    def delete(self, request, job_id):
        """
        Remove a job from the candidate's saved jobs.

        Args:
            request: The authenticated API request.
            job_id: ID of the job to remove.

        Returns:
            Response: Confirmation of removal.
        """
        candidate = get_object_or_404(
            Candidate.active_objects,
            user=request.user
        )

        saved_job = get_object_or_404(
            SavedJob,
            candidate=candidate,
            job_id=job_id
        )

        saved_job.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )



class RecommendedJobsAPIView(APIView):
    """
    Return skill-based job recommendations for candidates.
    """

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):
        """
        Retrieve jobs recommended for the authenticated candidate.
        """

        candidate = get_object_or_404(
            Candidate.active_objects,
            user=request.user
        )

        recommendations = get_recommended_jobs(candidate)

        response_data = []

        for item in recommendations:
            job_data = RecommendedJobSerializer(
                item['job']
            ).data

            job_data['match_percentage'] = (
                item['match_percentage']
            )

            job_data['matched_skills'] = (
                item['matched_skills']
            )

            job_data['missing_skills'] = (
                item['missing_skills']
            )

            job_data['salary_match_percentage'] = (
            item['salary_match_percentage']
            )

            job_data['experience_match_percentage'] = (
                item['experience_match_percentage']
            )

            job_data['location_match_percentage'] = (
                item['location_match_percentage']
            )

            job_data['overall_match_percentage'] = (
                item['overall_match_percentage']
            )

            response_data.append(job_data)

        return Response(
            {
                'total_recommendations': len(response_data),
                'results': response_data,
            },
            status=status.HTTP_200_OK
        )


class CandidateNotificationsAPIView(generics.ListAPIView):
    """
    Retrieve all notifications belonging to the authenticated candidate.
    """

    serializer_class = ApplicationNotificationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        """Return notifications for the current active candidate."""

        candidate = get_object_or_404(
            Candidate.active_objects,
            user=self.request.user
        )

        return (
            ApplicationNotification.objects
            .filter(candidate=candidate)
            .select_related('application', 'application__job')
            .order_by('-created_at')
        )

class UnreadNotificationsAPIView(generics.ListAPIView):
    """
    Retrieve unread notifications for the authenticated candidate.
    """

    serializer_class = ApplicationNotificationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        """
        Return unread notifications for the current active candidate.
        """

        candidate = get_object_or_404(
            Candidate.active_objects,
            user=self.request.user
        )

        return (
            ApplicationNotification.objects
            .filter(
                candidate=candidate,
                is_read=False
            )
            .select_related('application', 'application__job')
            .order_by('-created_at')
        )


class MarkNotificationReadAPIView(generics.UpdateAPIView):
    """
    Mark an individual candidate notification as read.
    """

    serializer_class = ApplicationNotificationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]
    lookup_field = 'notification_id'
    lookup_url_kwarg = 'notification_id'

    def get_queryset(self):
        """
        Return notifications belonging to the current active candidate.
        """

        candidate = get_object_or_404(
            Candidate.active_objects,
            user=self.request.user
        )

        return ApplicationNotification.objects.filter(
            candidate=candidate
        )

    def update(self, request, *args, **kwargs):
        """
        Mark the selected notification as read.
        """

        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])

        return Response(
            {
                'message': 'Notification marked as read.',
                'notification_id': notification.notification_id,
                'is_read': notification.is_read
            },
            status=status.HTTP_200_OK
        )

class MarkAllNotificationsReadAPIView(generics.GenericAPIView):
    """
    Mark all notifications belonging to the authenticated candidate as read.
    """

    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        """
        Return notifications belonging to the current active candidate.
        """

        candidate = get_object_or_404(
            Candidate.active_objects,
            user=self.request.user
        )

        return ApplicationNotification.objects.filter(
            candidate=candidate
        )

    def patch(self, request, *args, **kwargs):
        """
        Mark all unread notifications as read.
        """

        updated_count = self.get_queryset().filter(
            is_read=False
        ).update(is_read=True)

        return Response(
            {
                'message': 'All notifications marked as read.',
                'updated_count': updated_count
            },
            status=status.HTTP_200_OK
        )