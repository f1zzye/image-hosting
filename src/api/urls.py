from rest_framework import routers, permissions
from django.urls import path
from django.urls.conf import include

from api.views import ImagesViewSet, StatusView, TariffPlanView, UserTariffView


app_name = "api"

router = routers.DefaultRouter()

router.register("images", ImagesViewSet, basename="images")
router.register("tariffs", TariffPlanView, basename="tariffs")
router.register("user-tariffs", UserTariffView, basename="user-tariffs")


urlpatterns = [
    path("", include(router.urls)),
    path("status/", StatusView.as_view(), name="health"),
]
