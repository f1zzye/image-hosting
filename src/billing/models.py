from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TariffPlan(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        unique=True,
        help_text=_("Name of tariff: Basic, Premium, Corporate or Custom"),
    )
    description = models.TextField(
        _("description"),
        max_length=1024,
        null=True,
        blank=True,
        help_text=_("Description of tariff features"),
    )
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        default=0.00,
        help_text=_("Subscription price"),
    )
    is_built_in = models.BooleanField(
        _("is built-in"),
        default=False,
        help_text=_("Built-in tariff (Basic, Premium, Enterprise)"),
    )

    has_thumbnail_200px = models.BooleanField(
        _("has 200px thumbnail"), default=True, help_text=_("Available thumbnail 200px")
    )
    has_thumbnail_400px = models.BooleanField(
        _("has 400px thumbnail"),
        default=False,
        help_text=_("Available thumbnail 400px"),
    )

    has_original_photo = models.BooleanField(
        _("has original photo access"),
        default=False,
        help_text=_("Access to the original image size"),
    )
    has_binary_link = models.BooleanField(
        _("has binary link"),
        default=False,
        help_text=_("Ability to create temporary links"),
    )

    class Meta:
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_built_in"]),
        ]
        verbose_name = _("Tariff Plan")
        verbose_name_plural = _("Tariff Plans")
        ordering = ["price", "name"]

    def __str__(self):
        return self.name

    def get_available_thumbnail_sizes(self):
        sizes = []
        if self.has_thumbnail_200px:
            sizes.append(200)
        if self.has_thumbnail_400px:
            sizes.append(400)
        return sizes


class UserSubscription(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name=_("user"),
    )
    plan = models.ForeignKey(
        TariffPlan,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name=_("subscription plan"),
    )

    is_active = models.BooleanField(
        _("is active"), default=True, help_text=_("Is the subscription active")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("User Tariff")
        verbose_name_plural = _("User Tariffs")
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["user"]),
            models.Index(fields=["plan"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name}"

    @property
    def subscriber_name(self):
        return self.user.get_full_name()

    @property
    def subscription_plan_name(self):
        return self.plan.name
