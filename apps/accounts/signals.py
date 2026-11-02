from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.employers.models import Employer
from apps.candidates.models import Candidate


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender,instance,created, **kwargs):

    # Execute only when new user is created
    if not created:
        return

    # Create candidate profile
    if instance.role == 'CANDIDATE':

        Candidate.objects.get_or_create(
            user = instance,
            defaults={
                'full_name': (
                    instance.get_full_name().strip()
                    or instance.username
                )
            }
        )

    # Create Employer profile
    elif instance.role == "EMPLOYER":

        Employer.objects.get_or_create(
            user=instance,
            defaults={
                'company_name': f"{instance.username}'s Company",
                'location' : 'Not provided'
            }
        )