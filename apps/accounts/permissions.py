"""
Custom permission classes for role-based access control.

These permissions restrict API access based on the authenticated
user's role.
"""
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Allow access only to authenticated admin users
    """

    def has_permission(self,request,view):
        """
        Check whether the user has the ADMIN role

        Args:
            request: The incoming HTTP request.
            view: The API view being accessed

        Returns:
            bool: True if the user is an admin; Otherwise False
        """

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )



class IsEmployer(BasePermission):
    """
    Allow access only to authenticated employer users
    """

    def has_permission(self,request,view):
        """
        Check whether the user has the EMPLOYER role

        Args:
            request: The incoming HTTP request.
            view: The API view being accessed

        Returns:
            bool: True if the user is an employer; Otherwise False
        """

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'EMPLOYER'
        )


class IsCandidate(BasePermission):
    """
    Allow access only to authenticated candidate users
    """

    def has_permission(self,request,view):
        """
        Check whether the user has the CANDIDATE role

        Args:
            request: The incoming HTTP request.
            view: The API view being accessed

        Returns:
            bool: True if the user is a candidate; Otherwise False
        """

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'CANDIDATE'
        )

