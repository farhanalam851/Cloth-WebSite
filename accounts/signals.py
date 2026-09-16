from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    Ensures every User has a Profile, even ones created outside the
    storefront's registration form (e.g. `createsuperuser`, or a user
    added directly through the Django admin).
    """
    if created:
        Profile.objects.get_or_create(user=instance)
