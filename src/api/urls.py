from rest_framework import routers, permissions
from django.urls import path
from django.urls.conf import include

from api.views import ImagesViewSet, StatusView


app_name = "api"

router = routers.DefaultRouter()

router.register("images", ImagesViewSet, basename="images")


urlpatterns = [
    path("", include(router.urls)),
    path("status/", StatusView.as_view(), name="health"),
]
