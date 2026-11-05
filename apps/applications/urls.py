from django.urls import path

from .views import (
    ApplyForJobAPIView,
    MyApplicationsAPIView,
    ReceivedApplicationsAPIView,
    UpdateApplicationStatusAPIView
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


]
