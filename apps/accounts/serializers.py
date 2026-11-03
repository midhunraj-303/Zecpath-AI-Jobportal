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

    refresh = serializers.CharField()

    def validate_refresh(self, value):

        try:
            token = RefreshToken(value)

            # Check whether the token is already blacklisted
            if BlacklistedToken.objects.filter(
                token__jti=token['jti']
            ).exists():

                raise serializers.ValidationError(
                    "This refresh token has already been blacklisted."
                )

        except TokenError:
            raise serializers.ValidationError(
                "Invalid or expired refresh token."
            )

        return value

    def save(self, **kwargs):

        token = RefreshToken(
            self.validated_data['refresh']
        )

        token.blacklist()
