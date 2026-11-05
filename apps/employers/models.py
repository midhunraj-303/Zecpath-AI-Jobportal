
from django.conf import settings
from django.db import models
from django.utils import timezone

class ActiveProfileManager(models.Manager):
    """Return only profiles that have not been soft-deleted."""

    def get_queryset(self):
        """Build a queryset containing active profiles only.

        Returns:
            QuerySet: Profiles where is_deleted is False.
        """
        return super().get_queryset().filter(is_deleted=False)



class Employer(models.Model):
    """Store company profile information for an employer account."""

    objects = models.Manager()
    active_objects = ActiveProfileManager()
    
    class CompanySize(models.TextChoices):
        """Define the available company size categories."""

        SIZE_1_10 = '1-10', '1–10 employees'
        SIZE_11_50 = '11-50', '11–50 employees'
        SIZE_51_200 = '51-200', '51–200 employees'
        SIZE_201_500 = '201-500', '201–500 employees'
        SIZE_501_1000 = '501-1000', '501–1000 employees'
        SIZE_1000_PLUS = '1000+', '1000+ employees'

    employer_id = models.BigAutoField(primary_key=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employer_profile'
    )

    # Company information
    company_name = models.CharField(max_length=200)
    company_domain = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
        max_length=20,
        choices=CompanySize.choices,
        blank=True
    )
    company_description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=200)

    # Admin-controlled verification
    is_verified = models.BooleanField(default=False)

    # Profile lifecycle management
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def soft_delete(self):
        """Mark the employer profile as deleted without removing its data."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a previously soft-deleted employer profile."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def __str__(self):
        """Return the company name as the profile's display value."""
        return self.company_name




