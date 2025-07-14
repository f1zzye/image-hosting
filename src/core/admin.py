from django.contrib import admin
from .models import ContactUs


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "message"]
    search_fields = ["full_name", "email", "message"]
    ordering = ["-id"]
