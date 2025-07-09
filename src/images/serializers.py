from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Image, ImageThumbnail, TemporaryLink
from .services import ImageProcessingService

User = get_user_model()


class ImageThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for image thumbnails."""
    
    class Meta:
        model = ImageThumbnail
        fields = ['id', 'size', 'file', 'width', 'height', 'file_size', 'created_at']
        read_only_fields = ['id', 'width', 'height', 'file_size', 'created_at']


class ImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading new images."""
    
    class Meta:
        model = Image
        fields = ['id', 'original_image', 'file_size', 'width', 'height', 'created_at']
        read_only_fields = ['id', 'file_size', 'width', 'height', 'created_at']
    
    def validate_original_image(self, value):
        """Validate uploaded image format and size."""
        is_valid, error_message = ImageProcessingService.validate_image(value)
        if not is_valid:
            raise serializers.ValidationError(error_message)
        return value
    
    def create(self, validated_data):
        """Create image and generate thumbnails based on user's tariff."""
        # Set the user from request context
        validated_data['user'] = self.context['request'].user
        
        # Create the image instance
        image = super().create(validated_data)
        
        # Generate thumbnails asynchronously (in a real app, you might use Celery)
        try:
            ImageProcessingService.create_thumbnails_for_image(image)
        except Exception as e:
            # Log error but don't fail the upload
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create thumbnails for image {image.id}: {str(e)}")
        
        return image


class ImageListSerializer(serializers.ModelSerializer):
    """Serializer for listing user's images with thumbnails."""
    
    thumbnails = ImageThumbnailSerializer(many=True, read_only=True)
    user_can_access_original = serializers.SerializerMethodField()
    user_can_create_temp_links = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = [
            'id', 'original_image', 'file_size', 'width', 'height', 
            'created_at', 'updated_at', 'thumbnails', 
            'user_can_access_original', 'user_can_create_temp_links'
        ]
        read_only_fields = [
            'id', 'file_size', 'width', 'height', 'created_at', 'updated_at'
        ]
    
    def get_user_can_access_original(self, obj):
        """Check if user can access original image based on tariff."""
        try:
            if hasattr(obj.user, 'tariff') and obj.user.tariff and obj.user.tariff.is_active:
                return obj.user.tariff.plan.has_original_photo
        except AttributeError:
            pass
        return False
    
    def get_user_can_create_temp_links(self, obj):
        """Check if user can create temporary links based on tariff."""
        return ImageProcessingService.can_create_temporary_link(obj.user)


class TemporaryLinkCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating temporary links."""
    
    class Meta:
        model = TemporaryLink
        fields = ['id', 'expires_in_seconds', 'expires_at', 'created_at']
        read_only_fields = ['id', 'expires_at', 'created_at']
    
    def validate_expires_in_seconds(self, value):
        """Validate expiration time is within allowed range."""
        if not (300 <= value <= 30000):
            raise serializers.ValidationError(
                "Expiration time must be between 300 and 30000 seconds (5 minutes to 8.3 hours)"
            )
        return value
    
    def create(self, validated_data):
        """Create temporary link for the image."""
        image = self.context['image']
        user = self.context['request'].user
        
        # Validate user can create temporary links
        if not ImageProcessingService.can_create_temporary_link(user):
            raise serializers.ValidationError(
                "Your tariff plan does not support temporary links"
            )
        
        return ImageProcessingService.create_temporary_link(
            image=image,
            expires_in_seconds=validated_data['expires_in_seconds']
        )


class TemporaryLinkSerializer(serializers.ModelSerializer):
    """Serializer for temporary link details."""
    
    image_id = serializers.UUIDField(source='image.id', read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = TemporaryLink
        fields = [
            'id', 'image_id', 'expires_in_seconds', 'expires_at', 
            'is_used', 'used_at', 'created_at', 'is_expired', 'is_valid'
        ]
        read_only_fields = [
            'id', 'image_id', 'expires_at', 'is_used', 'used_at', 'created_at'
        ]
    
    def get_is_expired(self, obj):
        """Check if link is expired."""
        return obj.is_expired()
    
    def get_is_valid(self, obj):
        """Check if link is valid (not expired and not used)."""
        return obj.is_valid()


# Keep the original serializer for backward compatibility
class ImagesSerializer(serializers.ModelSerializer):
    """Legacy serializer for backward compatibility."""
    
    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]
