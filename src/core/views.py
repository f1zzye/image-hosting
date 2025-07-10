from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, ListView
from django.contrib import messages
from common.mixins import TitleMixin
from images.forms import ImageUploadForm
from billing.models import TariffPlan, UserTariff
from django.conf import settings


class IndexView(TitleMixin, TemplateView):
    template_name = "index.html"
    title = "PhotoHub - Premium Photo Hosting"

    def get(self, request):
        form = ImageUploadForm()
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, "Please sign in or create an account to upload photos.")
            return redirect("accounts:sign-in")

        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()
        return redirect("core:index")


class TariffPlansView(TitleMixin, LoginRequiredMixin, TemplateView):
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
                "premium_plan_id": settings.PREMIUM_TARIFF_ID,
                "enterprise_plan_id": settings.ENTERPRISE_TARIFF_ID,
            }
        )

        return context
