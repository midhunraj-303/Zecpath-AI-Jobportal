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

     
