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


class UserRegistrationAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self,request):
        serializer = UserRegistrationSerializer(
            data = request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            response_serializer = UserSerializer(user)

            return Response(
                {
                    "message": "User registered successfully",
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