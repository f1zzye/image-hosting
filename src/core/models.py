from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactUs(models.Model):
    full_name = models.CharField(_("Full Name"), max_length=100)
    email = models.EmailField()
    message = models.TextField(_("Message"))

    class Meta:
        verbose_name_plural = _("Contact Us")

    def __str__(self):
        return self.full_name
