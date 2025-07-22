from images.models import Image
from rest_framework import serializers


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_original_image(self, value):
        if value.content_type not in ['image/jpeg', 'image/png']:
            raise serializers.ValidationError('Only jpg, jpeg, png files are allowed.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        image = Image.objects.create(user=user, **validated_data)
        return image