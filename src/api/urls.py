from rest_framework import routers, permissions
from django.urls import path
from django.urls.conf import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from api.views import ImagesViewSet, StatusView, TariffPlanView, UserTariffView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = "api"


schema_view = get_schema_view(
    openapi.Info(
        title="Image-hosting API",
        default_version="v1",
        description="API for image-hosting",
        term_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="user@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()

router.register("images", ImagesViewSet, basename="images")
router.register("tariffs", TariffPlanView, basename="tariffs")
router.register("user-tariffs", UserTariffView, basename="user-tariffs")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.jwt")),
    path("status/", StatusView.as_view(), name="health"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger_docs"),
]
