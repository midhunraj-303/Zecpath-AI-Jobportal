from django.urls import path
from .views import (
    UserRegistrationAPIView,
    CurrentUserAPIView,
    LogoutAPIView,
    VerifyEmailAPIView,
    RoleTestAPIView,
    AdminTestAPIView,
    EmployerTestAPIView,
    CandidateTestAPIView
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

    path('logout/',
         LogoutAPIView.as_view(),
         name = 'user-logout'
    ),

    path(
        'verify-email/<int:user_id>/<str:token>/',
        VerifyEmailAPIView.as_view(),
        name='verify-email'
    ),

    path('test/role/',RoleTestAPIView.as_view()),
    path('test/admin/',AdminTestAPIView.as_view()),
    path('test/employer/',EmployerTestAPIView.as_view()),
    path('test/candidate/',CandidateTestAPIView.as_view()),
]



