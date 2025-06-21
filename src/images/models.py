import uuid
from typing import List, Tuple
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from django.urls import reverse


from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from faker import Faker


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("user"),
    )
    title = models.CharField(
        _("title"),
        max_length=150,
        blank=True,
        help_text=_("Optional title for the image"),
    )
    original_image = models.ImageField(
        _("original file"),
        upload_to="images/",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ],
        help_text=_("Original image file (JPG or PNG only)"),
    )

    file_size = models.PositiveIntegerField(
        _("file size"),
        null=True,
        blank=True,
        help_text=_("File size in bytes")
    )

    width = models.PositiveIntegerField(_("width"), null=True, blank=True)
    height = models.PositiveIntegerField(_("height"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        if self.original_image and not self.width:
            self.width = self.original_image.width
            self.height = self.original_image.height
            self.file_size = self.original_image.size
        super().save(*args, **kwargs)

    def get_user_tariff(self):
        return getattr(self.user, 'tariff', None)

    def get_absolute_url(self):
        return reverse('images:detail', kwargs={'pk': self.pk})


# class ImageThumbnail(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     image = models.ForeignKey(
#         Image,
#         on_delete=models.CASCADE,
#         related_name="thumbnails",
#         verbose_name=_("image"),
#     )
#     size = models.PositiveIntegerField(
#         _("size"),
#         help_text=_("Size of the thumbnail in pixels"),
#     )




