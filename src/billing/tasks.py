from django.utils import timezone
from .models import UserTariff, TariffPlan

from config.celery import app


@app.task
def process_expired_tariffs():
    try:
        expired_tariffs = UserTariff.objects.filter(
            expires_at__lte=timezone.now(), is_active=True
        ).exclude(plan__title="Basic")

        count = expired_tariffs.count()
        if count == 0:
            return "No expired tariffs to process"

        basic_plan = TariffPlan.objects.get(title="Basic", is_built_in=True)

        processed = 0
        for tariff in expired_tariffs:
            tariff.plan = basic_plan
            tariff.paypal_subscription_id = None
            tariff.expires_at = None
            tariff.save()
            processed += 1

        return f"Successfully processed {processed} tariffs"

    except TariffPlan.DoesNotExist:
        return "Error: Basic plan not found"
    except Exception as e:
        return f"Error processing tariffs: {str(e)}"
