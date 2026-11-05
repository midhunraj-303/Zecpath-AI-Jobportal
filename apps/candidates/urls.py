
from django.urls import path

from .views import CandidateProfileAPIView


urlpatterns = [
    path(
        'profile/',
        CandidateProfileAPIView.as_view(),
        name='candidate-profile'
    ),
]
