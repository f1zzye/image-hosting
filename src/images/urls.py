from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ImageViewSet, download_via_temporary_link

app_name = 'images'

# Create DRF router
router = DefaultRouter()
router.register(r'', ImageViewSet, basename='image')

urlpatterns = [
    # DRF API routes
    path('api/', include(router.urls)),
    
    # Temporary link download endpoint
    path('download/<uuid:link_id>/', download_via_temporary_link, name='download-temporary-link'),
]