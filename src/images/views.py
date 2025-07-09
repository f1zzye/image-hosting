import logging
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Image, TemporaryLink
from .serializers import (
    ImageUploadSerializer, 
    ImageListSerializer, 
    TemporaryLinkCreateSerializer,
    TemporaryLinkSerializer
)
from .permissions import TariffBasedImagePermission, IsOwnerOrReadOnly
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


class ImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing images with tariff-based permissions.
    
    Provides:
    - list: Get user's images with thumbnails
    - create: Upload new image and generate thumbnails
    - retrieve: Get single image details
    - destroy: Delete image
    - generate_temporary_link: Create temporary download link (Enterprise only)
    """
    
    permission_classes = [IsAuthenticated, TariffBasedImagePermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Return only current user's images."""
        if getattr(self, 'swagger_fake_view', False):
            return Image.objects.none()
            
        return Image.objects.filter(user=self.request.user).prefetch_related('thumbnails')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ImageUploadSerializer
        elif self.action in ['list', 'retrieve']:
            return ImageListSerializer
        return ImageListSerializer
    
    def create(self, request, *args, **kwargs):
        """Upload a new image and generate thumbnails based on user's tariff."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            image = serializer.save()
            
            # Return created image with thumbnails
            response_serializer = ImageListSerializer(image, context={'request': request})
            
            return Response(
                {
                    'image': response_serializer.data,
                    'message': 'Image uploaded successfully',
                    'thumbnails_generated': len(image.thumbnails.all())
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error uploading image for user {request.user.id}: {str(e)}")
            return Response(
                {'error': 'Failed to upload image', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request, *args, **kwargs):
        """List user's images with tariff plan information."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add user's tariff information to response
        permission_handler = TariffBasedImagePermission()
        tariff_features = permission_handler.get_user_tariff_features(request.user)
        
        return Response({
            'images': serializer.data,
            'tariff_features': tariff_features,
            'total_images': len(serializer.data)
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Get single image details with user's access permissions."""
        image = self.get_object()
        serializer = self.get_serializer(image)
        
        # Add user's tariff information
        permission_handler = TariffBasedImagePermission()
        tariff_features = permission_handler.get_user_tariff_features(request.user)
        
        return Response({
            'image': serializer.data,
            'tariff_features': tariff_features
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete image and all associated thumbnails."""
        image = self.get_object()
        image_id = str(image.id)
        
        try:
            # Delete image (thumbnails will be deleted via CASCADE)
            image.delete()
            
            return Response(
                {'message': f'Image {image_id} deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {str(e)}")
            return Response(
                {'error': 'Failed to delete image', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='temporary-link')
    def generate_temporary_link(self, request, pk=None):
        """
        Generate a temporary download link for the image.
        
        Only available for Enterprise users.
        """
        image = self.get_object()
        
        # Check if user can create temporary links
        if not ImageProcessingService.can_create_temporary_link(request.user):
            return Response(
                {
                    'error': 'Temporary links not available',
                    'detail': 'Your tariff plan does not support temporary links. Upgrade to Enterprise.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create temporary link
        serializer = TemporaryLinkCreateSerializer(
            data=request.data, 
            context={'request': request, 'image': image}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            temp_link = serializer.save()
            
            # Return link details
            response_serializer = TemporaryLinkSerializer(temp_link)
            
            return Response(
                {
                    'temporary_link': response_serializer.data,
                    'download_url': request.build_absolute_uri(
                        f'/api/images/download/{temp_link.id}/'
                    ),
                    'message': 'Temporary link created successfully'
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating temporary link for image {image.id}: {str(e)}")
            return Response(
                {'error': 'Failed to create temporary link', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='download')
    def download_original(self, request, pk=None):
        """
        Download original image file.
        
        Only available for Premium/Enterprise users.
        """
        image = self.get_object()
        
        # Check if user can access original images
        try:
            if hasattr(request.user, 'tariff') and request.user.tariff and request.user.tariff.is_active:
                if not request.user.tariff.plan.has_original_photo:
                    return Response(
                        {
                            'error': 'Original image access not available',
                            'detail': 'Your tariff plan does not support original image downloads. Upgrade to Premium or Enterprise.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except AttributeError:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            response = HttpResponse(
                image.original_image.read(),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{image.original_image.name}"'
            return response
            
        except Exception as e:
            logger.error(f"Error downloading image {image.id}: {str(e)}")
            return Response(
                {'error': 'Failed to download image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def download_via_temporary_link(request, link_id):
    """
    Download image via temporary link.
    
    This is a function-based view for temporary link downloads.
    """
    try:
        temp_link = get_object_or_404(TemporaryLink, id=link_id)
        
        # Check if link is valid
        if not temp_link.is_valid():
            if temp_link.is_expired():
                return HttpResponse('Link has expired', status=410)
            elif temp_link.is_used:
                return HttpResponse('Link has already been used', status=410)
        
        # Mark link as used
        temp_link.mark_as_used()
        
        # Return the image file
        image = temp_link.image
        response = HttpResponse(
            image.original_image.read(),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{image.original_image.name}"'
        
        logger.info(f"Image {image.id} downloaded via temporary link {link_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error downloading via temporary link {link_id}: {str(e)}")
        return HttpResponse('Download failed', status=500)
