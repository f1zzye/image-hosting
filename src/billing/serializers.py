from billing.models import TariffPlan, UserTariff
from rest_framework import serializers

from accounts.serializers import UserSerializer


class TariffPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffPlan
        fields = [
            "title",
            "description",
            "price",
            "has_thumbnail_200px",
            "has_thumbnail_400px",
            "has_original_photo",
            "has_binary_link",
        ]


class UserTariffSerializer(serializers.ModelSerializer):
    plan_details = TariffPlanSerializer(source="plan", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)

    class Meta:
        model = UserTariff
        fields = [
            "id",
            "user",
            "user_details",
            "plan",
            "plan_details",
            "is_active",
            "created_at",
            "updated_at",
        ]
