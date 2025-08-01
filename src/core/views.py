from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, ListView
from django.contrib import messages
from common.mixins import TitleMixin, CacheMixin
from images.forms import ImageUploadForm
from billing.models import TariffPlan, UserTariff
from django.conf import settings
from datetime import datetime

from images.models import Image

from accounts.models import Profile
from rest_framework.exceptions import PermissionDenied

from .models import ContactUs
from bot.bot import send_contact_notification

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
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)


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


class ProfileView(LoginRequiredMixin, TitleMixin, CacheMixin, TemplateView):
    template_name = "core/profile.html"
    title = "Profile - PhotoHub"
    login_url = "accounts:sign-in"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        cache_key = f"profile_context_{user.id}"
        cache_time = 30

        cached_data = self.set_get_cache(None, cache_key, cache_time)

        if cached_data:
            context.update(cached_data)
            return context

        user_images = Image.objects.filter(user=user)
        total_photos = user_images.count()

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = None

        user_plan_info = get_user_plan_info(user)

        try:
            user_tariff = UserTariff.objects.get(user=user)
            expires_at = user_tariff.expires_at
            if expires_at is not None:
                now = datetime.now(expires_at.tzinfo)
                days_left = (expires_at - now).days
                if days_left < 0:
                    days_left = 0
            else:
                days_left = None
        except UserTariff.DoesNotExist:
            days_left = None

        cache_data = {
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
            "days_left": days_left,
        }

        self.set_get_cache(cache_data, cache_key, cache_time)

        context.update(cache_data)
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


class ContactUsView(TemplateView):
    template_name = "core/contacts.html"


class AjaxContactView(View):
    def get(self, request, *args, **kwargs):
        full_name = request.GET["full_name"]
        email = request.GET["email"]
        message = request.GET["message"]

        ContactUs.objects.create(
            full_name=full_name,
            email=email,
            message=message,
        )

        send_contact_notification(full_name, email, message)

        context = {"bool": True, "message": "Your message has been sent successfully."}
        return JsonResponse({"context": context})


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


class Handler403(TitleMixin, TemplateView):
    template_name = "403.html"
    title = "403 Forbidden"


class Handler404(TitleMixin, TemplateView):
    template_name = "404.html"
    title = "404 Not Found"


class Handler500(TitleMixin, TemplateView):
    template_name = "500.html"
    title = "500 Internal Server Error"


class Handler502(TitleMixin, TemplateView):
    template_name = "502.html"
    title = "502 Bad Gateway"


class Handler503(TitleMixin, TemplateView):
    template_name = "503.html"
    title = "503 Service Unavailable"
