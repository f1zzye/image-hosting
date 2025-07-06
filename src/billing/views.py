from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from common.mixins import TitleMixin

from billing.models import TariffPlan, UserTariff


class UpgradeTariff(TitleMixin, LoginRequiredMixin, View):
    title: str = "Upgrade Tariff"

    def get(self, request, tariff_id, new_plan) -> HttpResponse:
        current_tariff = get_object_or_404(
            UserTariff, user=request.user, is_active=True
        )

        new_plan = get_object_or_404(TariffPlan, title=new_plan)

        current_tariff.plan = new_plan
        current_tariff.paypal_subscription_id = tariff_id
        current_tariff.save()

        context = {"tariff_plan": new_plan, "title": self.title}
        return render(request, "billing/upgrade_tariff.html", context)
