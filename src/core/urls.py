from django.urls import include, path

from core.views import IndexView, TariffPlansView

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("pricing/", TariffPlansView.as_view(), name="pricing"),
]
