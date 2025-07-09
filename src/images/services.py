import logging
import uuid
from datetime import timedelta
from io import BytesIO
from typing import List, Tuple

from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image as PILImage

from .models import Image, ImageThumbnail, TemporaryLink

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """Service class to handle image validation, thumbnail generation, and optimization."""
    
    ALLOWED_FORMATS = {'JPEG', 'PNG'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_image(image_file) -> Tuple[bool, str]:
        """
        Validate image format and size.
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            if image_file.size > ImageProcessingService.MAX_FILE_SIZE:
                return False, "File size exceeds 10MB limit"
            
            # Check format using PIL
            with PILImage.open(image_file) as img:
                if img.format not in ImageProcessingService.ALLOWED_FORMATS:
                    return False, f"Unsupported format. Only {', '.join(ImageProcessingService.ALLOWED_FORMATS)} are allowed"
                
                # Verify image can be processed
                img.verify()
                
            return True, ""
            
        except Exception as e:
            logger.error(f"Image validation error: {str(e)}")
            return False, "Invalid image file"
    
    @staticmethod
    def get_thumbnail_sizes_for_user(user) -> List[int]:
        """
        Get available thumbnail sizes based on user's tariff plan.
        
        Args:
            user: User instance
            
        Returns:
            List of thumbnail sizes (heights) in pixels
        """
        # Try to get user's active tariff
        try:
            if hasattr(user, 'tariff') and user.tariff and user.tariff.is_active:
                return user.tariff.plan.get_available_thumbnail_sizes()
        except AttributeError:
            pass
        
        # Default to basic plan (200px only)
        return [200]
    
    @staticmethod
    def generate_thumbnail(original_image, height: int) -> Tuple[ContentFile, int, int, int]:
        """
        Generate a thumbnail with the specified height, maintaining aspect ratio.
        
        Args:
            original_image: Original image file
            height: Target height in pixels
            
        Returns:
            Tuple of (ContentFile, width, height, file_size)
        """
        try:
            # Reset file pointer
            original_image.seek(0)
            
            with PILImage.open(original_image) as img:
                # Convert to RGB if necessary (for PNG transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate new dimensions maintaining aspect ratio
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                new_width = int(height * aspect_ratio)
                
                # Resize image
                resized = img.resize((new_width, height), PILImage.Resampling.LANCZOS)
                
                # Save to bytes
                output = BytesIO()
                resized.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                # Create ContentFile
                thumbnail_content = ContentFile(
                    output.getvalue(),
                    name=f'thumb_{height}px_{uuid.uuid4().hex[:8]}.jpg'
                )
                
                return thumbnail_content, new_width, height, len(output.getvalue())
                
        except Exception as e:
            logger.error(f"Thumbnail generation error: {str(e)}")
            raise ValueError(f"Failed to generate thumbnail: {str(e)}")
    
    @staticmethod
    def create_thumbnails_for_image(image_instance: Image) -> List[ImageThumbnail]:
        """
        Create all required thumbnails for an image based on user's tariff.
        
        Args:
            image_instance: Image model instance
            
        Returns:
            List of created ImageThumbnail instances
        """
        thumbnails = []
        
        try:
            # Get required thumbnail sizes
            sizes = ImageProcessingService.get_thumbnail_sizes_for_user(image_instance.user)
            
            for size in sizes:
                # Check if thumbnail already exists
                existing = ImageThumbnail.objects.filter(
                    image=image_instance, 
                    size=size
                ).first()
                
                if existing:
                    logger.info(f"Thumbnail {size}px already exists for image {image_instance.id}")
                    thumbnails.append(existing)
                    continue
                
                # Generate thumbnail
                thumbnail_file, width, height, file_size = ImageProcessingService.generate_thumbnail(
                    image_instance.original_image, 
                    size
                )
                
                # Create thumbnail record
                thumbnail = ImageThumbnail.objects.create(
                    image=image_instance,
                    size=size,
                    file=thumbnail_file,
                    width=width,
                    height=height,
                    file_size=file_size
                )
                
                thumbnails.append(thumbnail)
                logger.info(f"Created thumbnail {size}px for image {image_instance.id}")
                
        except Exception as e:
            logger.error(f"Error creating thumbnails for image {image_instance.id}: {str(e)}")
            # Don't raise exception to avoid breaking image upload
            
        return thumbnails
    
    @staticmethod
    def can_create_temporary_link(user) -> bool:
        """
        Check if user can create temporary links based on tariff plan.
        
        Args:
            user: User instance
            
        Returns:
            Boolean indicating if user can create temporary links
        """
        try:
            if hasattr(user, 'tariff') and user.tariff and user.tariff.is_active:
                return user.tariff.plan.has_binary_link
        except AttributeError:
            pass
        
        return False
    
    @staticmethod
    def create_temporary_link(image: Image, expires_in_seconds: int = 3600) -> TemporaryLink:
        """
        Create a temporary link for image download.
        
        Args:
            image: Image instance
            expires_in_seconds: Link expiration time in seconds (default 1 hour)
            
        Returns:
            TemporaryLink instance
        """
        # Validate user can create temporary links
        if not ImageProcessingService.can_create_temporary_link(image.user):
            raise ValueError("User's tariff plan does not support temporary links")
        
        # Validate expiration time (5 minutes to 8.3 hours)
        if not (300 <= expires_in_seconds <= 30000):
            raise ValueError("Expiration time must be between 300 and 30000 seconds")
        
        return TemporaryLink.objects.create(
            image=image,
            user=image.user,
            expires_in_seconds=expires_in_seconds,
            expires_at=timezone.now() + timedelta(seconds=expires_in_seconds)
        )