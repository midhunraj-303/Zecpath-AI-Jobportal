
"""
Custom permission classes for role-based access control.

These permissions restrict API access based on the authenticated
user's role and account status.
"""

from rest_framework.permissions import BasePermission


class BaseRolePermission(BasePermission):
    """
    Base permission class for role-based access control.

    Subclasses must define the required_role attribute.
    """

    required_role = None

    def has_permission(self, request, view):
        """
        Check authentication, account status, and user role.

        Args:
            request: The incoming HTTP request.
            view: The API view being accessed.

        Returns:
            bool: True if the user satisfies all requirements.
        """

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.is_verified
            and user.role == self.required_role
        )


class IsAdmin(BaseRolePermission):
    """
    Allow access only to active, verified admin users.
    """

    required_role = 'ADMIN'


class IsEmployer(BaseRolePermission):
    """
    Allow access only to active, verified employer users.
    """

    required_role = 'EMPLOYER'


class IsCandidate(BaseRolePermission):
    """
    Allow access only to active, verified candidate users.
    """

    required_role = 'CANDIDATE'
