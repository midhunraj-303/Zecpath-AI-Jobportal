
from django.urls import path

from .views import (
    CandidateProfileAPIView,
    ResumeAPIView,
    CandidateResumeDownloadAPIView
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
    

]
