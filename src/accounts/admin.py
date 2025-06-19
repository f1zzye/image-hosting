from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Profile
from django.utils.translation import gettext_lazy as _


class ProfileAdmin(admin.StackedInline):
    model = Profile


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileAdmin]
    list_display = (
        "email",
        "username",
        "get_full_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_display_links = ("email", "username")
    search_fields = ("first_name", "last_name", "email", "username")
    ordering = ("-date_joined", "email")
    readonly_fields = ("date_joined", "last_login")
    fieldsets = (
        (_("Authentication"), {"fields": ("email", "username", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important Dates"),
            {
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    def get_full_name(self, obj):
        full_name = obj.get_full_name()
        return full_name if full_name else "-"
