from django.db import models
from django.conf import settings


class Candidate(models.Model):

    # primary key
    candidate_id = models.BigAutoField(
        primary_key = True
    )

    #Relationship witht User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )

    # Candidate Information
    full_name = models.CharField(
        max_length=200
    )

    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True
    )

    skills = models.TextField(
        blank=True
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.full_name
