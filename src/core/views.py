from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, ListView
from django.contrib import messages
from common.mixins import TitleMixin
from images.forms import ImageUploadForm
from billing.models import TariffPlan, UserTariff
from django.conf import settings

from images.models import Image

from accounts.models import Profile
from rest_framework.exceptions import PermissionDenied


ALLOWED_PLANS = {
    "Basic": ["Basic"],
    "Premium": ["Basic", "Premium"],
    "Enterprise": ["Basic", "Premium", "Enterprise"],
}


class IndexView(TitleMixin, TemplateView):
    template_name = "index.html"
    title = "PhotoHub - Premium Photo Hosting"

    def get(self, request):
        form = ImageUploadForm()
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.warning(
                request, "Please sign in or create an account to upload photos."
            )
            return redirect("accounts:sign-in")

        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()
        return redirect("core:profile")


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


class ProfileView(TitleMixin, TemplateView):
    template_name = "core/profile.html"
    title = "Profile - PhotoHub"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_images = Image.objects.filter(user=user)
        total_photos = user_images.count()

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = None

        user_plan_info = get_user_plan_info(user)

        context.update(
            {
                "user_profile": user,
                "user_images": user_images,
                "total_photos": total_photos,
                "user_email": user.email,
                "user_username": user.username,
                "user_plan": user_plan_info["plan_title"],
                "member_since": user.get_member_since,
                "user_subscription_plan": user_plan_info["plan_title"],
                "has_binary_link": user_plan_info["has_binary_link"],
                "allowed_plans": ALLOWED_PLANS,
                "profile": profile,
            }
        )
        return context


class ImageDownloadPermissionCheckView(LoginRequiredMixin, View):

    def get(self, request, image_id):
        image = get_object_or_404(Image, id=image_id)

        if image.user != request.user:
            raise PermissionDenied("You don't have permission to access this image")

        user_plan_info = get_user_plan_info(request.user)

        available_options = get_available_download_options_from_plan(
            user_plan_info["plan_object"]
        )

        return JsonResponse(
            {
                "image_id": str(image.id),
                "user_plan": user_plan_info["plan_title"],
                "has_binary_link": user_plan_info["has_binary_link"],
                "available_options": available_options,
                "allowed_plans": ALLOWED_PLANS,
            }
        )


def get_user_plan_info(user):
    try:
        user_tariff = (
            UserTariff.objects.select_related("plan")
            .only("plan__title", "plan__has_binary_link")
            .get(user=user)
        )
        return {
            "plan_title": user_tariff.plan.title,
            "has_binary_link": user_tariff.plan.has_binary_link,
            "plan_object": user_tariff.plan,
        }
    except UserTariff.DoesNotExist:
        return {"plan_title": "Basic", "has_binary_link": False, "plan_object": None}


def get_available_download_options_from_plan(plan):
    if not plan:
        return [{"size": "200", "formats": ["png", "jpeg"], "type": "image"}]

    options = []

    if plan.has_thumbnail_200px:
        options.append({"size": "200", "formats": ["png", "jpeg"], "type": "image"})

    if plan.has_thumbnail_400px:
        options.append({"size": "400", "formats": ["png", "jpeg"], "type": "image"})

    if plan.has_original_photo:
        options.append(
            {"size": "original", "formats": ["png", "jpeg"], "type": "image"}
        )

    return options
