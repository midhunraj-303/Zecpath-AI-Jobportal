
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import (
    IsCandidate,
    IsEmployer
)
from apps.candidates.models import Candidate
from apps.jobs.models import Job

from .models import Application
from .serializers import ApplicationSerializer

from apps.employers.models import Employer

class ApplyForJobAPIView(generics.CreateAPIView):
    """Allow authenticated candidates to apply for active jobs."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def create(self, request, *args, **kwargs):
        """Create a job application for the authenticated candidate.

        Args:
            request: The HTTP request containing job_id and application data.

        Returns:
            Response: Created application details or validation errors.
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
            Candidate,
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

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        application = serializer.save(
            candidate=candidate,
            job=job
        )

        return Response(
            self.get_serializer(application).data,
            status=status.HTTP_201_CREATED
        )


class MyApplicationsAPIView(generics.ListAPIView):
    """List applications submitted by the authenticated candidate."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

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
