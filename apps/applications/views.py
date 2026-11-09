
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import (
    IsCandidate,
    IsEmployer,
    IsAdmin
)
from apps.candidates.models import Candidate
from apps.jobs.models import Job

from .models import Application
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusUpdateSerializer
)

from apps.employers.models import Employer
from pathlib import Path

from django.core.files.base import ContentFile
from django.db import transaction

from django.http import FileResponse
from rest_framework.views import APIView
from utils.pagination import StandardResultsSetPagination


class ApplyForJobAPIView(generics.CreateAPIView):
    """Allow authenticated candidates to apply for active jobs."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]


    def create(self, request, *args, **kwargs):
        """Create an application with an independent resume copy.

        Use an uploaded application-specific resume when provided.
        Otherwise, copy the candidate's latest profile resume.

        Args:
            request: The authenticated candidate's API request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The created application or a validation error.

        Raises:
            serializers.ValidationError: If submitted data is invalid.
        """
        job_id = request.data.get('job_id')

        if not job_id:
            return Response(
                {'error': 'job_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        job = get_object_or_404(
            Job,
            job_id=job_id,
            is_active=True
        )

        candidate = get_object_or_404(
            Candidate.active_objects,
            user=request.user
        )

        if Application.objects.filter(
            candidate=candidate,
            job=job
        ).exists():
            return Response(
                {'error': 'You have already applied for this job.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_resume = serializer.validated_data.get('resume')

        # Use the profile resume when no custom resume is uploaded.
        if uploaded_resume is None:
            if not candidate.resume:
                return Response(
                    {
                        'error': (
                            'Please upload a resume to your profile '
                            'or provide one for this application.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not candidate.resume.storage.exists(candidate.resume.name):
                return Response(
                    {
                        'error': (
                            'Your profile resume is missing. '
                            'Please upload it again.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        application = None
        resume_storage = Application._meta.get_field('resume').storage

        try:
            with transaction.atomic():  #application record and its resume copy to be handled as one database transaction 
                # Create the application.
                application = serializer.save(
                    candidate=candidate,
                    job=job
                )

                # Copy the profile resume if no custom resume was uploaded.
                if uploaded_resume is None:
                    profile_resume_name = candidate.resume.name

                    candidate.resume.open('rb')

                    try:
                        resume_content = ContentFile(
                            candidate.resume.read()
                        )
                    finally:
                        candidate.resume.close()

                    application.resume.save(
                        Path(profile_resume_name).name,
                        resume_content,
                        save=True
                    )

                

        except Exception:
            # Remove a newly stored file if the database operation fails.
            if application and application.resume:
                resume_storage.delete(application.resume.name)

            raise

        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_201_CREATED
        )




class MyApplicationsAPIView(generics.ListAPIView):
    """List applications submitted by the authenticated candidate."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return applications belonging to the current candidate.

        Returns:
            QuerySet: The candidate's job applications.
        """

        candidate = get_object_or_404(
            Candidate,
            user=self.request.user
        )

        return (
            Application.objects
            .filter(candidate=candidate)
            .select_related('candidate', 'job')
            .order_by('-applied_at')
        )







class ReceivedApplicationsAPIView(generics.ListAPIView):
    """List applications received for the employer's own jobs."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return applications for jobs owned by the logged-in employer.

        Returns:
            QuerySet: Applications received for the employer's jobs.
        """

        employer = get_object_or_404(
            Employer,
            user=self.request.user
        )

        return (
            Application.objects
            .filter(job__employer=employer)
            .select_related('candidate', 'job')
            .order_by('-applied_at')
        )



class UpdateApplicationStatusAPIView(generics.UpdateAPIView):
    """Allow employers to update application statuses for their own jobs."""

    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    lookup_field = 'application_id'
    lookup_url_kwarg = 'application_id'

    http_method_names = ['patch', 'options', 'head']

    def get_queryset(self):
        """Return applications belonging to the logged-in employer.

        Returns:
            QuerySet: Applications for jobs owned by this employer.
        """
        return (
            Application.objects
            .filter(job__employer__user=self.request.user)
            .select_related('candidate', 'job', 'job__employer')
        )


class ApplicationResumeDownloadAPIView(APIView):
    """Allow employers and admins to download application resumes."""

    permission_classes = [
        IsAuthenticated,
        IsEmployer | IsAdmin
    ]

    def get(self, request, application_id):
        """Download the resume attached to a specific application.

        Employers can access applications for their own jobs.
        Admins can access applications belonging to any employer.

        Args:
            request: The authenticated API request.
            application_id: The ID of the application.

        Returns:
            FileResponse: The application resume as a download.

        Raises:
            Http404: If the application or resume is not available.
        """
        if request.user.role == 'ADMIN':
            queryset = Application.objects.all()
        else:
            queryset = Application.objects.filter(
                job__employer__user=request.user
            )

        application = get_object_or_404(
            queryset,
            application_id=application_id
        )

        if not application.resume:
            return Response(
                {'error': 'No resume is attached to this application.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not application.resume.storage.exists(
            application.resume.name
        ):
            return Response(
                {'error': 'The resume file could not be found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        filename = Path(application.resume.name).name

        return FileResponse(
            application.resume.open('rb'),
            as_attachment=True,
            filename=filename
        )