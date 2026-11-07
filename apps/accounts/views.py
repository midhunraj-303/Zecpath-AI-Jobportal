from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    LogoutSerializer
)
from django.shortcuts import get_object_or_404
from apps.accounts.models import User
from apps.accounts.tokens import email_verification_token
from services.email_service import send_verification_email

from apps.accounts.permissions import (
    IsAdmin,
    IsEmployer,
    IsCandidate
)

class UserRegistrationAPIView(APIView):
    """
    Register a new user and send an email verification link.

    Newly registered users remain inactive until their email
    address has been verified.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate registration data, create the user, and send
        an email verification link.

        Args:
            request: The incoming HTTP request.

        Returns:
            Response: Registration details with HTTP 201,
            or validation errors with HTTP 400.
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            send_verification_email(user)

            response_serializer = UserSerializer(user)

            return Response(
                {
                    "message": (
                        "Registration successful. "
                        "Please check your email to activate your account."
                    ),
                    "user": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CurrentUserAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        serializer = UserSerializer(request.user)

        return Response({
            "message" : "User details retained successfully",
            "user": serializer.data
        })


class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()

        return Response(
            {"message":"Logout successful"},
            status=status.HTTP_200_OK
        )



class VerifyEmailAPIView(APIView):
    """
    Verify a user's email address and activate their account.

    This endpoint accepts a user ID and verification token.
    If the token is valid, the user's email is marked as verified
    and their account is activated.
    """

    permission_classes = [AllowAny]

    def get(self, request, user_id, token):
        """
        Validate the email verification token and activate the user.

        Args:
            request: The incoming HTTP request.
            user_id: The primary key of the user account.
            token: The email verification token.

        Returns:
            Response: A success response if verification succeeds,
            or an error response if the token is invalid or expired.

        Raises:
            Http404: If no user exists with the supplied user ID.
        """

        user = get_object_or_404(
            User,
            user_id=user_id
        )

        if user.is_verified and user.is_active:
            return Response(
                {
                    "message": "Email is already verified."
                },
                status=status.HTTP_200_OK
            )

        if not email_verification_token.check_token(user, token):
            return Response(
                {
                    "error": "Invalid or expired verification link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = True
        user.is_active = True

        user.save(
            update_fields=[
                'is_verified',
                'is_active',
                'updated_at'
            ]
        )

        return Response(
            {
                "message": (
                    "Email verified successfully. "
                    "Your account is now active."
                )
            },
            status=status.HTTP_200_OK
        )


class RoleTestAPIView(APIView):
    """
    Test role-based access control for authenticated users

    Only users with the required role required role can access this endpoint

    """

    permission_classes = [IsAuthenticated]

    def get(self,request):
        """
        Return the authenticated user's role.

        Args:
            request: The imcoming HTTP request.

        Returns:
            Response: The user's role and access message.
        """

        return Response({
            'message': "Authentication successful",
            'username': request.user.username,
            'role': request.user.role,
        })


class AdminTestAPIView(APIView):
    """
    Test access restricted to admin users.
    """

    permission_classes = [IsAdmin]

    def get(self,request):
        """Return a success message for admin users"""
        return Response({"message": "Welcome, Admin"})


class EmployerTestAPIView(APIView):
    """Test access restricted to employer users."""

    permission_classes = [IsEmployer]

    def get(self,request):
        """Return a success message for employer users"""

        return Response({"message": "Welcome, Employer"})


class CandidateTestAPIView(APIView):
    """Test access restricted to candidate users."""

    permission_classes = [IsCandidate]

    def get(self, request):
        """Return a success message for candidate users."""

        return Response({"message": "Welcome, Candidate"})
    