from django.db import models
from django.conf import settings

# Create your models here.



class Employer(models.Model):

    # Primary Key
    employer_id = models.BigAutoField(
        primary_key=True
    )

    # Relationship with user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile"
    )

    # Company Information

    company_name = models.CharField(
        max_length=200
    )

    company_description = models.TextField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    location = models.CharField(
        max_length=200
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.company_name
     
