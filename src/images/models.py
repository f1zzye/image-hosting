import uuid
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("user"),
    )
    original_image = models.ImageField(
        _("original file"),
        upload_to="images/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        help_text=_("Original image file (JPG or PNG only)"),
    )
    file_size = models.PositiveIntegerField(
        _("file size"), null=True, blank=True, help_text=_("File size in bytes")
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
        return f"{self.user.username} - Image {str(self.id)[:8]}"

    def save(self, *args, **kwargs):
        if self.original_image and not self.width:
            try:
                self.width = self.original_image.width
                self.height = self.original_image.height
                self.file_size = self.original_image.size
            except (AttributeError, ValueError):
                pass
        super().save(*args, **kwargs)

    def get_user_tariff(self):
        return getattr(self.user, "tariff", None)

    def get_absolute_url(self):
        return reverse("images:detail", kwargs={"pk": self.pk})


class ImageThumbnail(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="thumbnails",
        verbose_name=_("image"),
    )

    size = models.PositiveIntegerField(
        _("size"),
        help_text=_("Height of thumbnail in pixels (200, 400, etc.)"),
    )

    file = models.ImageField(
        _("thumbnail file"),
        upload_to="thumbnails/%Y/%m/%d/",
    )

    width = models.PositiveIntegerField(_("width"))
    height = models.PositiveIntegerField(_("height"))
    file_size = models.PositiveIntegerField(_("file size"))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Image Thumbnail")
        verbose_name_plural = _("Image Thumbnails")
        unique_together = [["image", "size"]]
        ordering = ["size"]
        indexes = [
            models.Index(fields=["image", "size"]),
        ]

    def __str__(self):
        return f"{str(self.image.id)[:8]} - {self.size}px"


class TemporaryLink(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="temporary_links",
        verbose_name=_("image"),
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="temporary_links",
        verbose_name=_("user"),
    )

    expires_in_seconds = models.PositiveIntegerField(
        _("expires in seconds"),
        validators=[
            MinValueValidator(300),
            MaxValueValidator(30000),
        ],
        help_text=_("Link expiration time in seconds (300-30000)"),
    )

    expires_at = models.DateTimeField(_("expires at"))
    is_used = models.BooleanField(_("is used"), default=False)
    used_at = models.DateTimeField(_("used at"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Temporary Link")
        verbose_name_plural = _("Temporary Links")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["expires_at", "is_used"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Link for Image {str(self.image.id)[:8]} (expires: {self.expires_at})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                seconds=self.expires_in_seconds
            )
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_expired() and not self.is_used

    def mark_as_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=["is_used", "used_at"])
