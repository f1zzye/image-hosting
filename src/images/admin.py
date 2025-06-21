from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Image, ImageThumbnail, TemporaryLink


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = [
        "id_short",
        "user",
        "image_preview",
        "created_at",
    ]
    list_filter = [
        "created_at",
        "user",
    ]
    search_fields = [
        "user__username",
        "id",
    ]
    readonly_fields = [
        "id",
        "file_size",
        "width",
        "height",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]

    def id_short(self, obj):
        return str(obj.id)[:8]

    id_short.short_description = _("ID")

    def image_preview(self, obj):
        if obj.original_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.original_image.url,
            )
        return _("No image")

    image_preview.short_description = _("Preview")


@admin.register(ImageThumbnail)
class ImageThumbnailAdmin(admin.ModelAdmin):
    list_display = [
        "id_short",
        "image_id_short",
        "size",
        "thumbnail_preview",
        "created_at",
    ]
    list_filter = [
        "size",
        "created_at",
    ]
    readonly_fields = [
        "id",
        "width",
        "height",
        "file_size",
        "created_at",
    ]
    ordering = ["-created_at"]

    def id_short(self, obj):
        return str(obj.id)[:8]

    id_short.short_description = _("ID")

    def image_id_short(self, obj):
        return str(obj.image.id)[:8]

    image_id_short.short_description = _("Image ID")

    def thumbnail_preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.file.url,
            )
        return _("No thumbnail")

    thumbnail_preview.short_description = _("Preview")


@admin.register(TemporaryLink)
class TemporaryLinkAdmin(admin.ModelAdmin):
    list_display = [
        "id_short",
        "image_id_short",
        "user",
        "expires_in_seconds",
        "status_display",
        "created_at",
    ]
    list_filter = [
        "is_used",
        "created_at",
    ]
    readonly_fields = [
        "id",
        "expires_at",
        "created_at",
    ]
    ordering = ["-created_at"]

    def id_short(self, obj):
        return str(obj.id)[:8]

    id_short.short_description = _("ID")

    def image_id_short(self, obj):
        return str(obj.image.id)[:8]

    image_id_short.short_description = _("Image ID")

    def status_display(self, obj):
        if not obj.expires_at:
            return "⏸️ Pending"
        if obj.is_used:
            return "🔒 Used"
        elif obj.is_expired():
            return "⏰ Expired"
        else:
            return "✅ Active"

    status_display.short_description = _("Status")
