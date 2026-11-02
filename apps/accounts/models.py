from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):

    def create_superuser(self, username, email, password, **extra_fields):
        
        extra_fields.setdefault('role','ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_varified', True)
        
        return super().create_superuser(
            username, 
            email, 
            password, 
            **extra_fields
            )


class User(AbstractUser):

    class Role(models.TextChoices):

        ADMIN = 'ADMIN', 'Admin'
        EMPLOYER = 'EMPLOYER', 'Employer'
        CANDIDATE = 'CANDIDATE', 'Candidate'

    # Primary Key
    user_id = models.BigAutoField(primary_key=True)

    # User Information
    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    # Role management
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE
    )

    # Account Verification
    is_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # Custom Manager
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} - {self.role}" 

    