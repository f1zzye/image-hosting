from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView

from common.mixins import TitleMixin

from billing.models import TariffPlan, UserTariff


class IndexView(TitleMixin, TemplateView):
    template_name = "index.html"
    title = "PhotoHub - Premium Photo Hosting"


class SubscriptionPlansView(TitleMixin, LoginRequiredMixin, TemplateView):
    template_name = "core/pricing.html"
    title = "Subscription Plans - PhotoHub"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        plans = TariffPlan.objects.filter(is_built_in=True).order_by("price")

        plans_dict = {plan.title: plan for plan in plans}

        try:
            user_subscription = UserTariff.objects.select_related("plan").get(
                user=self.request.user
            )
            context["current_subscription"] = user_subscription
        except UserTariff.DoesNotExist:
            context["current_subscription"] = None

        context.update(
            {
                "plans": plans,
                "basic_plan": plans_dict.get("Basic"),
                "premium_plan": plans_dict.get("Premium"),
                "enterprise_plan": plans_dict.get("Enterprise"),
            }
        )

        return context
