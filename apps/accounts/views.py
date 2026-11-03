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
    UserSerializer
)


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

    