
"""
Views for employer profile management.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import IsEmployer
from .models import Employer
from .serializers import EmployerSerializer


class EmployerProfileAPIView(APIView):
    """
    Retrieve and update the authenticated employer's profile.
    """

    permission_classes = [IsEmployer]

    def get_object(self, user):
        """
        Retrieve the employer profile belonging to the user.

        Args:
            user: The authenticated employer user.

        Returns:
            Employer: The employer profile.
        """
        return Employer.objects.get(user=user)

    def get(self, request):
        """
        Retrieve the authenticated employer's profile.
        """
        employer = self.get_object(request.user)
        serializer = EmployerSerializer(employer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Completely update the employer profile.
        """
        employer = self.get_object(request.user)
        serializer = EmployerSerializer(
            employer,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        """
        Partially update the employer profile.
        """
        employer = self.get_object(request.user)
        serializer = EmployerSerializer(
            employer,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
