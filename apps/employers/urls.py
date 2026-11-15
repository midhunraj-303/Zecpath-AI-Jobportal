from django.urls import path
from .views import (
    EmployerProfileAPIView,
    EmployerApplicationStatsAPIView,
)
urlpatterns = [
    path(
        'profile/',
        EmployerProfileAPIView.as_view(),
        name='employer-profile'
    ),

    path(
        'dashboard/application-stats/',
        EmployerApplicationStatsAPIView.as_view(),
        name='employer-application-stats'
    ),
]