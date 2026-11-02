from rest_framework import serializers
from .models import User

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

