
from django.urls import path

from .views import (
    ApplyForJobAPIView,
    MyApplicationsAPIView,
    ReceivedApplicationsAPIView,
    UpdateApplicationStatusAPIView,
    ApplicationResumeDownloadAPIView,
    ApplicationStatusHistoryAPIView
)

urlpatterns = [
    path(
        '',
        ApplyForJobAPIView.as_view(),
        name='apply-for-job'
    ),

    path(
        'my-applications/',
        MyApplicationsAPIView.as_view(),
        name='my-applications'
    ),

    path(
        'received/',
        ReceivedApplicationsAPIView.as_view(),
        name='received-applications'
    ),

    path(
        '<int:application_id>/status/',
        UpdateApplicationStatusAPIView.as_view(),
        name='update-application-status'
    ),

    path(
        '<int:application_id>/resume/',
        ApplicationResumeDownloadAPIView.as_view(),
        name='application-resume-download'
    ),

    path(
        'history/<int:application_id>/',
        ApplicationStatusHistoryAPIView.as_view(),
        name='application-status-history'
    ),

]
