import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from billing.models import TariffPlan, UserTariff

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_basic_tariff(sender, instance, created, **kwargs):
    if created:
        try:
            basic_plan = TariffPlan.objects.get(title="Basic", is_built_in=True)
            UserTariff.objects.create(
                user=instance,
                plan=basic_plan,
                is_active=True,
            )
        except TariffPlan.DoesNotExist:
            logging.error(
                f"Basic plan not found when creating user {instance.username}"
            )
