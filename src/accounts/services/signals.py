from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from accounts.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, "profile"):
        Profile.objects.create(user=instance)
