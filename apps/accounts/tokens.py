
"""
Token generation utilities for account email verification.

This module provides a customized token generator that creates
time-sensitive verification tokens for user accounts.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generate secure tokens for verifying user email addresses.

    The token depends on the user's ID, email address, activation
    status, verification status, and token timestamp.

    Changing any of these values invalidates the existing token.
    """

    def _make_hash_value(self, user, timestamp):
        """
        Generate the hash input used to create the verification token.

        Args:
            user: The user instance for which the token is generated.
            timestamp: The token generation timestamp.

        Returns:
            str: A string containing user-specific values used
            to generate the token hash.
        """

        return (
            str(user.user_id)
            + str(timestamp)
            + str(user.is_active)
            + str(user.is_verified)
            + str(user.email)
        )


email_verification_token = EmailVerificationTokenGenerator()
