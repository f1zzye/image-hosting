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


class TariffPlanView(ModelViewSet):
    queryset = TariffPlan.objects.all()
    serializer_class = TariffPlanSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["title", "description"]
    ordering_fields = ["price", "title"]


class UserTariffView(ModelViewSet):
    queryset = UserTariff.objects.all()
    serializer_class = UserTariffSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ["user__username", "plan__title"]
    ordering_fields = ["-created_at"]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserTariff.objects.none()

        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return UserTariff.objects.none()

        return UserTariff.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('plan', 'user')
