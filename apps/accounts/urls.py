from django.urls import path
from .views import (
    UserRegistrationAPIView,
    CurrentUserAPIView
)

urlpatterns = [
    path(
        'register/',
        UserRegistrationAPIView.as_view(),
        name='user-register'
    ),

    path(
        'me/',
        CurrentUserAPIView.as_view(),
        name='current-user'
    ),
]

