"""
Tests for job management and query optimization.
"""

from django.test import TestCase

from django.contrib.auth import get_user_model

from apps.employers.models import Employer

from .models import Job, JobStatus, Skill

from .views import PublicJobQueryMixin

User = get_user_model()


class PublicJobQueryOptimizationTest(TestCase):
    """Test database query optimization for public job listings."""

    @classmethod
    def setUpTestData(cls):
        """Create reusable test data."""

        cls.user = User.objects.create_user(
            username='test_employer',
            email='test@example.com',
            password='TestPassword123!'
        )

        cls.employer = Employer.objects.create(
            user=cls.user,
            company_name='Test Company',
            location='Kochi, Kerala'
        )

        cls.skill = Skill.objects.create(
            skill_name='Python',
            approval_status=Skill.ApprovalStatus.APPROVED
        )

        cls.jobs = Job.objects.bulk_create([
            Job(
                employer=cls.employer,
                job_title=f'Test Developer {number}',
                description='Test job description',
                location='Kochi, Kerala',
                status=JobStatus.PUBLISHED
            )
            for number in range(1, 4)
        ])

        for job in cls.jobs:
            job.skills.add(cls.skill)


    def test_public_job_queryset_uses_optimized_queries(self):
        """Verify employer and skills are fetched without extra queries."""

        with self.assertNumQueries(2):
            jobs = list(PublicJobQueryMixin().get_public_jobs())

            for job in jobs:
                _ = job.employer.company_name
                _ = list(job.skills.all())