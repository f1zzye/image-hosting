from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import TariffPlan, UserTariff


@admin.register(TariffPlan)
class TariffPlanAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "price",
        "is_built_in",
        "has_thumbnail_200px",
        "has_thumbnail_400px",
        "has_original_photo",
        "has_binary_link",
        "users_count",
    ]
    list_filter = [
        "is_built_in",
        "has_thumbnail_200px",
        "has_thumbnail_400px",
        "has_original_photo",
        "has_binary_link",
        "price",
    ]
    search_fields = ["title", "description"]
    ordering = ["price", "title"]

    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("title", "description", "price", "is_built_in")},
        ),
        (
            _("Features"),
            {
                "fields": (
                    "has_thumbnail_200px",
                    "has_thumbnail_400px",
                    "has_original_photo",
                    "has_binary_link",
                )
            },
        ),
    )

    def users_count(self, obj):
        return obj.users.filter(is_active=True).count()

    users_count.short_description = _("Active Users")

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_built_in:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(UserTariff)
class UserTariffAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "paypal_subscription_id", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "plan", "created_at", "updated_at"]
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "plan__title",
    ]
    ordering = ["-created_at"]
    readonly_fields = ["paypal_subscription_id", "created_at", "updated_at"]

    autocomplete_fields = ["user"]

    fieldsets = (
        (_("Tariff Details"), {"fields": ("user", "plan", "is_active")}),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["activate_subscriptions", "deactivate_subscriptions"]

    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} tariffs were successfully activated.")

    activate_subscriptions.short_description = _("Activate selected tariffs")

    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} tariffs were successfully deactivated.")

    deactivate_subscriptions.short_description = _("Deactivate selected tariffs")


class UserSubscriptionInline(admin.StackedInline):
    model = UserTariff
    extra = 0
    max_num = 1
    fields = ["plan", "is_active"]
    autocomplete_fields = ["plan"]
