from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class TariffPlan(models.Model):
    title = models.CharField(
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
        help_text=_("Tariff price"),
    )
    is_built_in = models.BooleanField(
        _("is built-in"),
        default=False,
        help_text=_("Built-in tariff (Basic, Premium, Enterprise)"),
    )

    paypal_plan_id = models.CharField(
        max_length=300, unique=True, null=True, blank=True
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
            models.Index(fields=["title"]),
            models.Index(fields=["is_built_in"]),
        ]
        verbose_name = _("Tariff Plan")
        verbose_name_plural = _("Tariff Plans")
        ordering = ["price", "title"]

    def __str__(self):
        return self.title

    def get_available_thumbnail_sizes(self):
        sizes = []
        if self.has_thumbnail_200px:
            sizes.append(200)
        if self.has_thumbnail_400px:
            sizes.append(400)
        return sizes


class UserTariff(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="tariff",
        verbose_name=_("user"),
    )
    plan = models.ForeignKey(
        TariffPlan,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name=_("tariff plan"),
    )

    paypal_subscription_id = models.CharField(max_length=300, null=True, blank=True)

    is_active = models.BooleanField(
        _("is active"), default=True, help_text=_("Is the tariff active")
    )

    expires_at = models.DateTimeField(
        _("expires at"),
        null=True,
        blank=True,
        help_text=_("When the subscription expires (null for Basic plan)"),
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
        return f"{self.user.get_full_name()} - {self.plan.title} subscription"

    @property
    def subscriber_name(self):
        return self.user.get_full_name()

    @property
    def subscription_plan_title(self):
        return self.plan.title

    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def is_basic_plan(self):
        return self.plan.title == "Basic"
