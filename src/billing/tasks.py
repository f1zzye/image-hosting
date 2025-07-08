from datetime import timedelta
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserTariff, TariffPlan
from django.utils.translation import gettext as _
from config.celery import app
from django.conf import settings
from django.core.mail import EmailMessage


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
            tariff.expiration_notification_sent = False
            tariff.save()
            processed += 1

        return f"Successfully processed {processed} tariffs"

    except TariffPlan.DoesNotExist:
        return "Error: Basic plan not found"
    except Exception as e:
        return f"Error processing tariffs: {str(e)}"


@app.task
def send_subscription_expiring_email_task(user_tariff_id):
    try:
        user_tariff = UserTariff.objects.select_related("user", "plan").get(
            id=user_tariff_id
        )

        if user_tariff.expiration_notification_sent:
            return f"Notification not needed for {user_tariff.user.email}"

        user = user_tariff.user
        days_left = user_tariff.days_until_expiry

        mail_subject = _("Your PhotoHub subscription is expiring soon")

        domain = settings.SITE_URL

        message = render_to_string(
            "emails/subscription_expiring.html",
            {
                "user": user,
                "days_left": days_left,
                "plan_title": user_tariff.subscription_plan_title,
                "domain": domain,
            },
        )

        email = EmailMessage(
            subject=mail_subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send()

        user_tariff.expiration_notification_sent = True
        user_tariff.save(update_fields=["expiration_notification_sent"])

        return f"Email sent to {user.email} ({days_left} days left)"

    except UserTariff.DoesNotExist:
        return f"UserTariff with id {user_tariff_id} not found"


@app.task
def check_expiring_subscriptions():
    try:
        target_date = timezone.now() + timedelta(days=3)
        start_of_target_day = target_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_of_target_day = start_of_target_day + timedelta(days=1)

        expiring_subscriptions = UserTariff.objects.filter(
            is_active=True,
            expires_at__isnull=False,
            expires_at__gte=start_of_target_day,
            expires_at__lt=end_of_target_day,
            expiration_notification_sent=False,
        ).exclude(plan__title="Basic")

        sent_count = 0

        for subscription in expiring_subscriptions:
            send_subscription_expiring_email_task.delay(subscription.id)
            sent_count += 1

        return f"Scheduled {sent_count} expiration notifications"

    except Exception as e:
        return f"Error checking expiring subscriptions: {str(e)}"
