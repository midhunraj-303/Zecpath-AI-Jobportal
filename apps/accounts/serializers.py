from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            'user_id',
            'username',
            'email',
            'phone',
            'role',
            'is_verified',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'user_id',
            'role',
            'is_verified',
            'created_at',
            'updated_at',
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only = True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User

        fields = [
            'user_id',
            'username',
            'email',
            'password',
            'phone',
            'role',
        ]

        read_only_fields = [
            'user_id'
        ]

    def validate_role(self,value):

        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Admin registration is not allowed"
            )

        return value

    def create(self,validated_data):

        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user

class LogoutSerializer(serializers.Serializer):
    """
    Serializer for securely logging out an authenticated user.

    Validates the refresh token, verifies token ownership,
    and blacklists the token to prevent further use.
    """

    refresh = serializers.CharField()

    def validate_refresh(self, value):
        """
        Validate the refresh token and verify its ownership.

        Args:
            value: The refresh token submitted by the user.

        Returns:
            str: The validated refresh token.

        Raises:
            serializers.ValidationError: If the token is invalid,
                expired, blacklisted, or belongs to another user.
        """
        try:
            token = RefreshToken(value)

            request = self.context.get('request')

            if request is None or not request.user.is_authenticated:
                raise serializers.ValidationError(
                    "Authentication is required."
                )

            token_user_id = token.get('user_id')

            if str(token_user_id) != str(request.user.user_id):
                raise serializers.ValidationError(
                    "You cannot logout using another user's refresh token."
                )

            self._refresh_token = token

        except TokenError:
            raise serializers.ValidationError(
                "Invalid, expired, or already blacklisted refresh token."
            )

        return value

    def save(self, **kwargs):
        """
        Blacklist the validated refresh token.

        Returns:
            None
        """
        self._refresh_token.blacklist()