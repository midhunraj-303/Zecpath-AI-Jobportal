
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
    JobStatusUpdateAPIView
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

]
