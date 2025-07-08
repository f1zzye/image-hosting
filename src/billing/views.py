from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from common.mixins import TitleMixin
from datetime import timedelta
from django.utils import timezone
from .tasks import send_subscription_expiring_email_task
from .models import TariffPlan, UserTariff


class UpgradeTariff(TitleMixin, LoginRequiredMixin, View):
    title: str = "Upgrade Tariff"

    def get(self, request, tariff_id, new_plan) -> HttpResponse:
        current_tariff = get_object_or_404(
            UserTariff, user=request.user, is_active=True
        )

        new_plan_obj = get_object_or_404(TariffPlan, title=new_plan)

        current_tariff.plan = new_plan_obj
        current_tariff.paypal_subscription_id = tariff_id

        if new_plan != "Basic":
            current_tariff.expires_at = timezone.now() + timedelta(days=30)
        else:
            current_tariff.expires_at = None

        current_tariff.expiration_notification_sent = False
        current_tariff.save()

        context = {"tariff_plan": new_plan_obj, "title": self.title}
        return render(request, "billing/upgrade_tariff.html", context)
