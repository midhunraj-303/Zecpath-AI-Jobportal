
from django.urls import path

from .views import (
    CandidateProfileAPIView,
    ResumeAPIView,
    CandidateResumeDownloadAPIView,
    SavedJobsAPIView,
    SavedJobDetailAPIView,
    RecommendedJobsAPIView,
    CandidateNotificationsAPIView,
    UnreadNotificationsAPIView,
    MarkNotificationReadAPIView,
    MarkAllNotificationsReadAPIView,
    
)


urlpatterns = [
    path(
        'profile/',
        CandidateProfileAPIView.as_view(),
        name='candidate-profile'
    ),

    path('resume/',
         ResumeAPIView.as_view(),
         name='candidate-resume'
    ),

    path(
    'resume/download/',
    CandidateResumeDownloadAPIView.as_view(),
    name='candidate-resume-download'
    ),

    # Candidate Saved Jobs APIs
    path(
        'saved-jobs/',
        SavedJobsAPIView.as_view(),
        name='candidate-saved-jobs'
    ),

    path(
        'saved-jobs/<int:job_id>/',
        SavedJobDetailAPIView.as_view(),
        name='candidate-saved-job-detail'
    ),

    path(
        'recommended-jobs/',
        RecommendedJobsAPIView.as_view(),
        name='candidate-recommended-jobs'
    ),

    # Candidate Notification APIs

    path(
        'notifications/',
        CandidateNotificationsAPIView.as_view(),
        name='candidate-notifications'
    ),

    path(
        'notifications/unread/',
        UnreadNotificationsAPIView.as_view(),
        name='candidate-unread-notifications'
    ),

    path(
        'notifications/<int:notification_id>/read/',
        MarkNotificationReadAPIView.as_view(),
        name='candidate-mark-notification-read'
    ),

    path(
        'notifications/read-all/',
        MarkAllNotificationsReadAPIView.as_view(),
        name='candidate-mark-all-notifications-read'
    ),


]
