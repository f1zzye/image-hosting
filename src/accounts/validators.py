from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_birth_date(value):
    if value > timezone.now().date():
        raise ValidationError(_("Birth date cannot be in the future"))
