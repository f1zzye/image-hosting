from django.urls import path

from billing.views import UpgradeTariff

app_name = "billing"

urlpatterns = [
    path(
        "update-tariff/<str:tariff_id>/<str:new_plan>/",
        UpgradeTariff.as_view(),
        name="update_tariff",
    ),
]
