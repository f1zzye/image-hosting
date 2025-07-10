from django.conf import settings
from django.utils import timezone

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from .validators import validate_birth_date
from faker import Faker

from .managers import CustomUserManager

GENDER_CHOICES = (
    ("Undefined", "Undefined"),
    ("Male", "Male"),
    ("Female", "Female"),
)


class User(AbstractBaseUser, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Indicates whether the user can log in as an administrator."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,  # Изменить на False когда подключу активацию по емаилу
        help_text=_("Designates whether this user should be treated as active."),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["is_active", "is_staff"]),
        ]

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_member_since(self) -> str:
        return f"Member since {self.date_joined.strftime('%B %Y')}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        default="avatars/default-avatar.jpg",
        blank=True,
        null=True,
    )
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10, default="Undefined"
    )
    birth_date = models.DateField(
        _("birth date"), validators=[validate_birth_date], blank=True, null=True
    )

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
