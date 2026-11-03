
"""
Email-related services for the Zecpath application.

This module handles sending account verification emails to
newly registered users.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from apps.accounts.tokens import email_verification_token


def send_verification_email(user):
    """
    Send an email verification link to a registered user.

    Generates a time-sensitive verification token, constructs
    the verification URL, and sends it to the user's email address.

    Args:
        user: The User instance requiring email verification.

    Returns:
        None

    Raises:
        Exception: If the email backend fails to send the email.
    """

    token = email_verification_token.make_token(user)

    verification_path = reverse(
        'verify-email',
        kwargs={
            'user_id': user.user_id,
            'token': token
        }
    )

    verification_url = (
        f"{settings.FRONTEND_URL}{verification_path}"
    )

    subject = "Verify Your Zecpath Account"

    message = f"""
Hello {user.username},

Thank you for registering with Zecpath.

Please click the link below to verify your email address:

{verification_url}

This verification link will expire after the configured timeout.

If you did not create this account, please ignore this email.

Regards,
Zecpath Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )
