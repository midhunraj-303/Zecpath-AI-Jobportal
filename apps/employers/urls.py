from django.urls import path
from .views import EmployerProfileAPIView

urlpatterns = [
    path(
        'profile/',
        EmployerProfileAPIView.as_view(),
        name='employer-profile'
    ),
]