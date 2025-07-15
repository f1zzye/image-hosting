from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from images.models import Image
from images.serializers import ImagesSerializer
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAdminOrReadOnly
from rest_framework.views import APIView
from datetime import datetime, timezone
from billing.models import TariffPlan, UserTariff

from billing.serializers import TariffPlanSerializer, UserTariffSerializer

from loguru import logger


class StatusView(APIView):
    def get(self, request, *args, **kwargs):
        database_status: str = "OK"
        cache_status: str = "OK"

        health_status = {
            "status": status.HTTP_200_OK,
            "version": "1.0.0",
            "dependencies": {
                "database": database_status,
                "cache": cache_status,
            },
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }

        return Response(health_status, status=status.HTTP_200_OK)


class ImagesViewSet(ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    ordering_fields = ["created_at", "file_size"]
    ordering = ["-created_at"]

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error("Error retrieving image with id '{}': {}", kwargs.get("pk"), e)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error("Error listing images: {}", e)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TariffPlanView(ModelViewSet):
    queryset = TariffPlan.objects.all()
    serializer_class = TariffPlanSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["title", "description"]
    ordering_fields = ["price", "title"]

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                "Error retrieving tariff plan with id '{}': {}", kwargs.get("pk"), e
            )
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error("Error listing tariff plans: {}", e)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error("Error creating tariff plan: {}", e)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                "Error updating tariff plan with id '{}': {}", kwargs.get("pk"), e
            )
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                "Error deleting tariff plan with id '{}': {}", kwargs.get("pk"), e
            )
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserTariffView(ModelViewSet):
    queryset = UserTariff.objects.all()
    serializer_class = UserTariffSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["user__username", "plan__title"]
    ordering_fields = ["-created_at"]

    def get_queryset(self):
        try:
            if getattr(self, "swagger_fake_view", False):
                return UserTariff.objects.none()

            if (
                not hasattr(self.request, "user")
                or not self.request.user.is_authenticated
            ):
                return UserTariff.objects.none()

            return UserTariff.objects.filter(
                user=self.request.user, is_active=True
            ).select_related("plan", "user")
        except Exception as e:
            logger.error(
                "Error in UserTariffView.get_queryset for user '{}': {}",
                getattr(self.request, "user", None),
                e,
            )
            return UserTariff.objects.none()

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                "Error retrieving user tariff with id '{}': {}", kwargs.get("pk"), e
            )
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error("Error listing user tariffs: {}", e)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error("Error creating user tariff: {}", e)
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                "Error updating user tariff with id '{}': {}", kwargs.get("pk"), e
            )
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                "Error deleting user tariff with id '{}': {}", kwargs.get("pk"), e
            )
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
