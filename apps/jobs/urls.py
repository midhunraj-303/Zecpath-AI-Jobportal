
"""
URL patterns for job APIs.
"""

from django.urls import path

from .views import (
    JobListCreateAPIView,
    JobDetailAPIView,
    AdminJobListAPIView,
    AvailableJobListAPIView,
    AvailableJobDetailAPIView,
    AdminJobRestoreAPIView,
    JobStatusUpdateAPIView,
    FeaturedJobListAPIView,
    LatestJobListAPIView,
    SkillListCreateAPIView,
    SkillApprovalAPIView,
    PendingSkillListAPIView
)

urlpatterns = [
    path(
        '',
        JobListCreateAPIView.as_view(),
        name='job-list-create'
    ),

    path(
        '<int:job_id>/',
        JobDetailAPIView.as_view(),
        name='job-detail'
    ),

    path(
        'admin/',
        AdminJobListAPIView.as_view(),
        name='admin-job-list'
    ),

    path(
        'available/',
        AvailableJobListAPIView.as_view(),
        name='available-job-list'
    ),

    path(
        'available/<int:job_id>/',
        AvailableJobDetailAPIView.as_view(),
        name='available-job-detail'
    ),

    path(
        'admin/<int:job_id>/restore/',
        AdminJobRestoreAPIView.as_view(),
        name='admin-job-restore'
    ),

    path(
        '<int:job_id>/status/',
        JobStatusUpdateAPIView.as_view(),
        name='job-status-update'
    ),

    path(
        'available/featured/',
        FeaturedJobListAPIView.as_view(),
        name='featured-job-list'
    ),

    path(
        'available/latest/',
        LatestJobListAPIView.as_view(),
        name='latest-job-list'
    ),

    path(
        'skills/',
        SkillListCreateAPIView.as_view(),
        name='skill-list-create'
    ),

    path(
        'skills/<int:skill_id>/approval/',
        SkillApprovalAPIView.as_view(),
        name='skill-approval'
    ),

    path(
        'skills/pending/',
        PendingSkillListAPIView.as_view(),
        name='pending-skill-list'
    ),

]
