
"""
Views for job management.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)

from apps.accounts.permissions import (
    IsEmployer,
    IsAdmin,
)
from apps.employers.models import Employer

from .models import Job
from .serializers import JobSerializer

from utils.pagination import StandardResultsSetPagination
from django.utils.dateparse import parse_date

from django.db.models import Q  # Combine multiple conditions using OR

class JobListCreateAPIView(APIView):
    """
    Create jobs and list jobs for the authenticated employer.
    """

    permission_classes = [IsEmployer]

    def get(self, request):
        """
        Retrieve paginated jobs created by the authenticated employer.

        Args:
            request: The incoming HTTP request.

        Returns:
            Response: Paginated list of the employer's jobs.
        """

        try:
            employer = Employer.objects.get(user=request.user)
        except Employer.DoesNotExist:
            return Response(
                {"error": "Employer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        jobs = Job.objects.filter(
            employer=employer
        ).order_by('-created_at')

        paginator = StandardResultsSetPagination()
        paginated_jobs = paginator.paginate_queryset(
            jobs,
            request
        )

        serializer = JobSerializer(
            paginated_jobs,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )
    def post(self, request):
        """
        Create a job for the authenticated employer.

        Args:
            request: The incoming HTTP request.

        Returns:
            Response: Created job data or validation errors.
        """

        try:
            employer = Employer.active_objects.get(user=request.user)
        except Employer.DoesNotExist:
            return Response(
                {"error": "Employer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            job = serializer.save(employer=employer)

            return Response(
                {
                    "message": "Job created successfully.",
                    "job": JobSerializer(job).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class JobDetailAPIView(APIView):
    """
    Retrieve, update and delete an employer's individual job.
    """

    permission_classes = [IsAdmin | IsEmployer]


    def get_object(self, request, job_id):
        """
        Retrieve a job based on the user's role and ownership.

        Admin users can access any job. Employers can access only
        jobs belonging to their active employer profile.
        """

        if request.user.role == 'ADMIN':
            return Job.objects.get(job_id=job_id)

        employer = Employer.active_objects.get(user=request.user)

        return Job.objects.get(
            job_id=job_id,
            employer=employer
        )

    def get(self, request, job_id):
        """
        Retrieve a specific job belonging to the employer.
        """

        try:
            job = self.get_object(request, job_id)
        except (Job.DoesNotExist, Employer.DoesNotExist):
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobSerializer(job)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    
    def put(self, request, job_id):
        """
        Completely update a job belonging to the employer.

        Args:
            request: The incoming HTTP request.
            job_id: The primary key of the job.

        Returns:
            Response: Updated job data or an error response.
        """

        try:
            job = self.get_object(request, job_id)
        except (Job.DoesNotExist, Employer.DoesNotExist):
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobSerializer(
            job,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Job updated successfully.",
                    "job": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    
    def patch(self, request, job_id):
        """
        Partially update a job belonging to the employer.

        Args:
            request: The incoming HTTP request.
            job_id: The primary key of the job.

        Returns:
            Response: Updated job data or validation errors.
        """

        try:
            job = self.get_object(request, job_id)
        except (Job.DoesNotExist, Employer.DoesNotExist):
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobSerializer(
            job,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Job updated successfully.",
                    "job": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    
    def delete(self, request, job_id):
        """
        Delete a job belonging to the authenticated employer.

        Args:
            request: The incoming HTTP request.
            job_id: The primary key of the job.

        Returns:
            Response: Confirmation of deletion or an error response.
        """

        try:
            job = self.get_object(request, job_id)
        except (Job.DoesNotExist, Employer.DoesNotExist):
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        job.delete()

        return Response(
            {"message": "Job deleted successfully."},
            status=status.HTTP_200_OK
        )


class AdminJobListAPIView(APIView):
    """
    Allow administrators to view all jobs.
    """

    permission_classes = [IsAdmin]


    def get(self, request):
        """
        Retrieve paginated jobs posted by all employers.

        Args:
            request: The incoming HTTP request.

        Returns:
            Response: Paginated list of all job records.
        """

        jobs = Job.objects.select_related(  # Job model has a relationship with Employer, and Employer has a relationship with User
            'employer',
            'employer__user'
        ).order_by('-created_at')

        # pagination
        paginator = StandardResultsSetPagination()
        paginated_jobs = paginator.paginate_queryset(
            jobs,
            request
        )

        serializer = JobSerializer(
            paginated_jobs,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class AvailableJobListAPIView(APIView):
    """
    Allow public users to browse active job postings.
    """

    permission_classes = [AllowAny]


    def get(self, request):
        """
        Retrieve paginated active job postings for public users.

        Args:
            request: The incoming HTTP request.

        Returns:
            Response: Paginated list of active jobs.
        """

        jobs = Job.objects.filter(  #ensures inactive jobs are never publicly displayed.
            is_active=True
        ).select_related(           #efficiently retrieves employer information.
            'employer'
        ).order_by('-created_at')   #displays newest jobs first.

        
        # filter using Job role
        role = request.query_params.get('role')

        if role:
            jobs = jobs.filter(job_title__icontains=role)


        # Filter jobs by posting date
        posted_date = request.query_params.get('date')

        if posted_date:
            parsed_date = parse_date(posted_date)

            if parsed_date is None:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            jobs = jobs.filter(
                created_at__date=parsed_date
            )

        # Filter jobs by status
        job_status = request.query_params.get('status')

        if job_status:
            job_status = job_status.upper()

            if job_status == 'ACTIVE':
                jobs = jobs.filter(is_active=True)

            elif job_status == 'INACTIVE':
                jobs = jobs.filter(is_active=False)

            else:
                return Response(
                    {
                        "error": "Invalid status. Use ACTIVE or INACTIVE."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


        # Search jobs by keyword
        search_keyword = request.query_params.get('search')

        if search_keyword:
            jobs = jobs.filter(
                Q(job_title__icontains=search_keyword) |
                Q(description__icontains=search_keyword) |
                Q(location__icontains=search_keyword)
            )

        # pagination
        paginator = StandardResultsSetPagination()   #applies our reusable pagination settings.
        paginated_jobs = paginator.paginate_queryset(
            jobs,
            request
        )

        serializer = JobSerializer(
            paginated_jobs,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class AvailableJobDetailAPIView(APIView):
    """
    Allow public users to view an individual active job.
    """

    permission_classes = [AllowAny]

    def get(self, request, job_id):
        """
        Retrieve details of an active job.

        Args:
            request: The incoming HTTP request.
            job_id: The primary key of the requested job.

        Returns:
            Response: Job details or a not-found response.
        """

        try:
            job = Job.objects.select_related(
                'employer'
            ).get(
                job_id=job_id,
                is_active=True
            )
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobSerializer(job)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
