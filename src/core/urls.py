from django.urls import include, path

from core.views import (
    IndexView,
    TariffPlansView,
    ProfileView,
    ImageDownloadPermissionCheckView,
    ContactUsView,
    AjaxContactView,
)

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("pricing/", TariffPlansView.as_view(), name="pricing"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "api/images/<uuid:image_id>/download/",
        ImageDownloadPermissionCheckView.as_view(),
        name="download_permissions",
    ),
    path("contacts/", ContactUsView.as_view(), name="contacts"),
    path("ajax-contact-form/", AjaxContactView.as_view(), name="ajax-contact-form"),
]
