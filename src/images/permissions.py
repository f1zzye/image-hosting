from rest_framework import permissions
from .services import ImageProcessingService


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user
            
        # Write permissions are only allowed to the owner of the image.
        return obj.user == request.user


class CanAccessOriginalImage(permissions.BasePermission):
    """Permission to check if user can access original images based on tariff."""
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access original image based on their tariff plan."""
        try:
            user_tariff = request.user.user_tariffs.filter(is_active=True).first()
            if user_tariff and user_tariff.plan:
                return user_tariff.plan.has_original_photo
        except AttributeError:
            pass
        
        # Default: Basic plan users cannot access original images
        return False


class CanCreateTemporaryLinks(permissions.BasePermission):
    """Permission to check if user can create temporary links based on tariff."""
    
    def has_permission(self, request, view):
        """Check if user can create temporary links based on their tariff plan."""
        if not request.user or not request.user.is_authenticated:
            return False
            
        return ImageProcessingService.can_create_temporary_link(request.user)


class TariffBasedImagePermission(permissions.BasePermission):
    """
    Combined permission class that handles different access levels based on tariff plans.
    
    - Basic: 200px thumbnails only
    - Premium: 200px, 400px thumbnails + original access
    - Enterprise: All of Premium + temporary links
    """
    
    def has_permission(self, request, view):
        """Check basic authentication and permissions."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow all authenticated users to list and create images
        if view.action in ['list', 'create']:
            return True
            
        # For specific actions, check in has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions based on action and tariff."""
        # Only allow access to own images
        if obj.user != request.user:
            return False
        
        # Allow basic operations for all users
        if view.action in ['retrieve', 'destroy']:
            return True
            
        # Check specific action permissions
        if view.action == 'generate_temporary_link':
            return ImageProcessingService.can_create_temporary_link(request.user)
        
        return True
    
    def get_user_tariff_features(self, user):
        """Get user's tariff features for response customization."""
        try:
            if hasattr(user, 'tariff') and user.tariff and user.tariff.is_active:
                return {
                    'has_200px_thumbnail': user.tariff.plan.has_thumbnail_200px,
                    'has_400px_thumbnail': user.tariff.plan.has_thumbnail_400px,
                    'has_original_access': user.tariff.plan.has_original_photo,
                    'has_temporary_links': user.tariff.plan.has_binary_link,
                    'plan_name': user.tariff.plan.title
                }
        except AttributeError:
            pass
            
        # Default features for Basic plan
        return {
            'has_200px_thumbnail': True,
            'has_400px_thumbnail': False,
            'has_original_access': False,
            'has_temporary_links': False,
            'plan_name': 'Basic'
        }