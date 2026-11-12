
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

from .models import Job, JobStatus, Skill
from .serializers import JobSerializer,SkillSerializer

from utils.pagination import StandardResultsSetPagination
from django.utils.dateparse import parse_date

from django.db.models import Q  # Combine multiple conditions using OR

from django.utils import timezone


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
            employer = Employer.active_objects.get(user=request.user)
        except Employer.DoesNotExist:
            return Response(
                {"error": "Employer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        jobs = Job.objects.filter(
            employer=employer,
            is_deleted=False
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

        if job.is_deleted:
            return Response(
                {"error": "Job has already been deleted."},
                status=status.HTTP_404_NOT_FOUND
            )

        job.is_deleted = True
        job.deleted_at = timezone.now()

        job.save(
            update_fields=['is_deleted', 'deleted_at', 'updated_at']
        )

        return Response(
            {"message": "Job deleted successfully."},
            status=status.HTTP_200_OK
        )



class JobStatusUpdateAPIView(APIView):
    """
    Allow employers and administrators to update job statuses.
    """

    permission_classes = [IsAdmin | IsEmployer]

    # Define permitted status transitions.
    ALLOWED_TRANSITIONS = {
        JobStatus.DRAFT: [
            JobStatus.PUBLISHED
        ],
        JobStatus.PUBLISHED: [
            JobStatus.PAUSED,
            JobStatus.CLOSED
        ],
        JobStatus.PAUSED: [
            JobStatus.PUBLISHED,
            JobStatus.CLOSED
        ],
        JobStatus.CLOSED: [],
        JobStatus.EXPIRED: [],
    }

    def patch(self, request, job_id):
        """
        Update a job's lifecycle status.

        Employers can update only their own jobs.
        Administrators can update any job.

        Args:
            request: The incoming HTTP request.
            job_id: The primary key of the job.

        Returns:
            Response: Updated job data or an error response.
        """

        try:
            if request.user.role == 'ADMIN':
                job = Job.objects.get(
                    job_id=job_id,
                    is_deleted=False
                )
            else:
                employer = Employer.active_objects.get(
                    user=request.user
                )

                job = Job.objects.get(
                    job_id=job_id,
                    employer=employer,
                    is_deleted=False
                )

        except (Job.DoesNotExist, Employer.DoesNotExist):
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        if new_status not in JobStatus.values:
            return Response(
                {"error": "Invalid job status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_status = job.status

        if new_status == current_status:
            return Response(
                {"error": "Job already has this status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_statuses = self.ALLOWED_TRANSITIONS.get(
            current_status,
            []
        )

        if new_status not in allowed_statuses:
            return Response(
                {
                    "error": (
                        f"Cannot change job status from "
                        f"{current_status} to {new_status}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.status = new_status

        job.is_active = (
            new_status == JobStatus.PUBLISHED
        )

        if (
            new_status == JobStatus.PUBLISHED
            and job.published_at is None
        ):
            job.published_at = timezone.now()

        job.save(
            update_fields=[
                'status',
                'is_active',
                'published_at',
                'updated_at'
            ]
        )

        return Response(
            {
                "message": "Job status updated successfully.",
                "job": JobSerializer(job).data
            },
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


# Avoids repeating the same database filtering logic.
# Ensures deleted and unpublished jobs never appear publicly.
# Makes future discovery endpoints easier to maintain.
class PublicJobQueryMixin:
    """
    Provide a reusable queryset for publicly visible jobs.
    """

    def get_public_jobs(self):
        """
        Return published jobs that have not been deleted.
        """

        return Job.objects.filter(
            status=JobStatus.PUBLISHED,
            is_deleted=False
        ).select_related(
            'employer'
        )


class AvailableJobListAPIView(PublicJobQueryMixin,APIView):
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

        jobs = self.get_public_jobs().order_by('-created_at')


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

        # Filter jobs by experience range.
        min_experience = request.query_params.get(
            'min_experience'
        )

        max_experience = request.query_params.get(
            'max_experience'
        )

        if min_experience is not None:
            try:
                min_experience = int(min_experience)

                if min_experience < 0:
                    raise ValueError

            except (ValueError, TypeError):
                return Response(
                    {
                        'error': (
                            'min_experience must be a '
                            'non-negative integer.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if max_experience is not None:
            try:
                max_experience = int(max_experience)

                if max_experience < 0:
                    raise ValueError

            except (ValueError, TypeError):
                return Response(
                    {
                        'error': (
                            'max_experience must be a '
                            'non-negative integer.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if (
            min_experience is not None
            and max_experience is not None
            and min_experience > max_experience
        ):
            return Response(
                {
                    'error': (
                        'min_experience cannot be greater '
                        'than max_experience.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if min_experience is not None:
            jobs = jobs.filter(
                Q(max_experience__gte=min_experience) |
                Q(max_experience__isnull=True)
            )

        if max_experience is not None:
            jobs = jobs.filter(
                min_experience__lte=max_experience
            )

        # Filter jobs by publication status.
        job_status = request.query_params.get('status')

        if job_status:
            job_status = job_status.upper()

            if job_status not in ['ACTIVE', 'PUBLISHED']:
                return Response(
                    {
                        'error': (
                            'Invalid status. Public listings support '
                            'only ACTIVE or PUBLISHED.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Filter jobs by required skills.
        skill_parameter = request.query_params.get('skill')

        if skill_parameter:
            requested_skills = [
                skill.strip()           # Remove unnecessary spaces
                for skill in skill_parameter.split(',')     #Supports multiple skills
                if skill.strip()
            ]

            if requested_skills:
                jobs = jobs.filter(
                    skills__skill_name__in=requested_skills     #filters through the ManyToMany relationship.
                ).distinct()                    #prevents duplicate jobs when multiple requested skills match.

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
                status='PUBLISHED',
                is_deleted=False
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



class FeaturedJobListAPIView(PublicJobQueryMixin, APIView):
    """
    Return currently featured jobs for public discovery.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieve featured jobs that have not expired.
        """

        today = timezone.localdate()

        jobs = self.get_public_jobs().filter(
            is_featured=True                        #only jobs marked as featured
        ).filter(
            Q(featured_until__isnull=True) |        #no expiry date has been set
            Q(featured_until__gte=today)            #the expiry date has not passed
        ).order_by('-created_at')

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(jobs, request)

        serializer = JobSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )



# The newest job postings appear first.
# It uses the existing job_latest_listing_idx database index.
class LatestJobListAPIView(PublicJobQueryMixin, APIView):
    """
    Return the latest published jobs for public discovery.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieve the latest published jobs with pagination.
        """

        jobs = self.get_public_jobs().order_by(
            '-created_at'
        )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(jobs, request)

        serializer = JobSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )

    

class AdminJobRestoreAPIView(APIView):
    """
    Allow administrators to restore soft-deleted jobs.
    """

    permission_classes = [IsAdmin]

    def post(self, request, job_id):
        """
        Restore a previously soft-deleted job.

        Args:
            request: The incoming HTTP request.
            job_id: The primary key of the job.

        Returns:
            Response: Restoration confirmation or an error.
        """

        try:
            job = Job.objects.get(
                job_id=job_id,
                is_deleted=True
            )
        except Job.DoesNotExist:
            return Response(
                {"error": "Deleted job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        job.is_deleted = False
        job.deleted_at = None

        job.save(
            update_fields=[
                'is_deleted',
                'deleted_at',
                'updated_at'
            ]
        )

        return Response(
            {
                "message": "Job restored successfully.",
                "job": JobSerializer(job).data
            },
            status=status.HTTP_200_OK
        )




class SkillListCreateAPIView(APIView):
    """
    List approved skills and allow employers to suggest new skills.
    """

    def get_permissions(self):
        """
        Apply permissions according to the HTTP method.
        """

        if self.request.method == 'GET':
            return [AllowAny()]

        if self.request.method == 'POST':
            return [IsAuthenticated(), IsEmployer()]

        return [IsAuthenticated(), IsAdmin()]

    def get(self, request):
        """
        List approved and active skills.

        Supports searching skills by name using
        the 'search' query parameter.
        """
        skills = Skill.objects.filter(
            approval_status=Skill.ApprovalStatus.APPROVED,
            is_active=True
        )

        search_query = request.query_params.get('search')

        if search_query:
            skills = skills.filter(
                skill_name__icontains=search_query.strip()
            )

        skills = skills.order_by('skill_name')

        serializer = SkillSerializer(skills, many=True)

        return Response(serializer.data)

    def post(self, request):
        """
        Allow an employer to suggest a new skill.
        """

        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(
            created_by=request.user,
            approval_status=Skill.ApprovalStatus.PENDING
        )

        return Response(
            {
                'message': 'Skill submitted for admin approval.',
                'skill': serializer.data
            },
            status=status.HTTP_201_CREATED
        )



class SkillApprovalAPIView(APIView):
    """
    Allow administrators to approve, reject or deactivate skills.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, skill_id):
        """
        Update a skill's approval status or active state.
        """

        try:
            skill = Skill.objects.get(skill_id=skill_id)
        except Skill.DoesNotExist:
            return Response(
                {'error': 'Skill not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        approval_status = request.data.get('approval_status')
        is_active = request.data.get('is_active')

        if approval_status is None and is_active is None:
            return Response(
                {
                    'error': (
                        'Provide approval_status or is_active.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if approval_status is not None:
            valid_statuses = Skill.ApprovalStatus.values

            if approval_status not in valid_statuses:
                return Response(
                    {'error': 'Invalid approval status.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            skill.approval_status = approval_status

        if is_active is not None:
            if not isinstance(is_active, bool):
                return Response(
                    {'error': 'is_active must be true or false.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            skill.is_active = is_active

        skill.save()

        serializer = SkillSerializer(skill)

        return Response({
            'message': 'Skill updated successfully.',
            'skill': serializer.data
        })



class PendingSkillListAPIView(APIView):
    """
    Allow administrators to view skills awaiting approval.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        """
        Return all skills with pending approval status.
        """

        skills = Skill.objects.filter(
            approval_status=Skill.ApprovalStatus.PENDING
        ).order_by('-created_at')

        serializer = SkillSerializer(
            skills,
            many=True
        )

        return Response(serializer.data)