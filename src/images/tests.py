import tempfile
import uuid
from datetime import timedelta
from io import BytesIO

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image as PILImage

from billing.models import TariffPlan, UserTariff
from .models import Image, ImageThumbnail, TemporaryLink
from .services import ImageProcessingService

User = get_user_model()


def create_test_image(format='JPEG', size=(800, 600)):
    """Create a test image for testing purposes."""
    image = PILImage.new('RGB', size, color='red')
    img_io = BytesIO()
    image.save(img_io, format=format)
    img_io.seek(0)
    return img_io


class ImageProcessingServiceTest(TestCase):
    """Test cases for ImageProcessingService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create tariff plans
        self.basic_plan = TariffPlan.objects.create(
            title='Basic',
            price=0.00,
            has_thumbnail_200px=True,
            has_thumbnail_400px=False,
            has_original_photo=False,
            has_binary_link=False
        )
        
        self.premium_plan = TariffPlan.objects.create(
            title='Premium',
            price=9.99,
            has_thumbnail_200px=True,
            has_thumbnail_400px=True,
            has_original_photo=True,
            has_binary_link=False
        )
        
        self.enterprise_plan = TariffPlan.objects.create(
            title='Enterprise',
            price=19.99,
            has_thumbnail_200px=True,
            has_thumbnail_400px=True,
            has_original_photo=True,
            has_binary_link=True
        )
    
    def test_validate_image_valid_jpeg(self):
        """Test validation of valid JPEG image."""
        img_data = create_test_image('JPEG')
        uploaded_file = SimpleUploadedFile('test.jpg', img_data.getvalue(), content_type='image/jpeg')
        
        is_valid, error = ImageProcessingService.validate_image(uploaded_file)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_image_valid_png(self):
        """Test validation of valid PNG image."""
        img_data = create_test_image('PNG')
        uploaded_file = SimpleUploadedFile('test.png', img_data.getvalue(), content_type='image/png')
        
        is_valid, error = ImageProcessingService.validate_image(uploaded_file)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_image_too_large(self):
        """Test validation of oversized image."""
        # Create a very large image data
        large_data = b'x' * (11 * 1024 * 1024)  # 11MB
        uploaded_file = SimpleUploadedFile('large.jpg', large_data, content_type='image/jpeg')
        
        is_valid, error = ImageProcessingService.validate_image(uploaded_file)
        
        self.assertFalse(is_valid)
        self.assertIn("File size exceeds", error)
    
    def test_get_thumbnail_sizes_basic_user(self):
        """Test thumbnail sizes for basic user."""
        # Assign basic plan to user
        UserTariff.objects.create(
            user=self.user,
            plan=self.basic_plan,
            is_active=True
        )
        
        sizes = ImageProcessingService.get_thumbnail_sizes_for_user(self.user)
        
        self.assertEqual(sizes, [200])
    
    def test_get_thumbnail_sizes_premium_user(self):
        """Test thumbnail sizes for premium user."""
        # Assign premium plan to user
        UserTariff.objects.create(
            user=self.user,
            plan=self.premium_plan,
            is_active=True
        )
        
        sizes = ImageProcessingService.get_thumbnail_sizes_for_user(self.user)
        
        self.assertIn(200, sizes)
        self.assertIn(400, sizes)
    
    def test_can_create_temporary_link_enterprise(self):
        """Test temporary link permission for enterprise user."""
        # Assign enterprise plan to user
        UserTariff.objects.create(
            user=self.user,
            plan=self.enterprise_plan,
            is_active=True
        )
        
        can_create = ImageProcessingService.can_create_temporary_link(self.user)
        
        self.assertTrue(can_create)
    
    def test_can_create_temporary_link_basic(self):
        """Test temporary link permission for basic user."""
        # Assign basic plan to user
        UserTariff.objects.create(
            user=self.user,
            plan=self.basic_plan,
            is_active=True
        )
        
        can_create = ImageProcessingService.can_create_temporary_link(self.user)
        
        self.assertFalse(can_create)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImageModelTest(TestCase):
    """Test cases for Image model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_image_creation(self):
        """Test image creation with automatic dimension extraction."""
        img_data = create_test_image('JPEG', (800, 600))
        uploaded_file = SimpleUploadedFile('test.jpg', img_data.getvalue(), content_type='image/jpeg')
        
        image = Image.objects.create(
            user=self.user,
            original_image=uploaded_file
        )
        
        self.assertEqual(image.width, 800)
        self.assertEqual(image.height, 600)
        self.assertIsNotNone(image.file_size)
        self.assertEqual(str(image), f"{self.user.username} - Image {str(image.id)[:8]}")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImageAPITest(APITestCase):
    """Test cases for Image API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create basic tariff plan
        self.basic_plan = TariffPlan.objects.create(
            title='Basic',
            price=0.00,
            has_thumbnail_200px=True,
            has_thumbnail_400px=False,
            has_original_photo=False,
            has_binary_link=False
        )
        
        # Assign basic plan to user
        UserTariff.objects.create(
            user=self.user,
            plan=self.basic_plan,
            is_active=True
        )
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)
    
    def test_upload_image(self):
        """Test image upload via API."""
        img_data = create_test_image('JPEG')
        uploaded_file = SimpleUploadedFile('test.jpg', img_data.getvalue(), content_type='image/jpeg')
        
        url = '/api/images/'
        data = {'original_image': uploaded_file}
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertIn('message', response.data)
        self.assertIn('thumbnails_generated', response.data)
        
        # Verify image was created
        self.assertEqual(Image.objects.count(), 1)
        image = Image.objects.first()
        self.assertEqual(image.user, self.user)
    
    def test_list_images(self):
        """Test listing user's images."""
        # Create test image
        img_data = create_test_image('JPEG')
        uploaded_file = SimpleUploadedFile('test.jpg', img_data.getvalue(), content_type='image/jpeg')
        
        Image.objects.create(
            user=self.user,
            original_image=uploaded_file
        )
        
        url = '/api/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('images', response.data)
        self.assertIn('tariff_features', response.data)
        self.assertEqual(len(response.data['images']), 1)
    
    def test_upload_invalid_format(self):
        """Test upload with invalid image format."""
        # Create a text file pretending to be an image
        invalid_file = SimpleUploadedFile('test.txt', b'This is not an image', content_type='text/plain')
        
        url = '/api/images/'
        data = {'original_image': invalid_file}
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access the API."""
        self.client.force_authenticate(user=None)
        
        url = '/api/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TemporaryLinkTest(TestCase):
    """Test cases for TemporaryLink model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test image
        img_data = create_test_image('JPEG')
        uploaded_file = SimpleUploadedFile('test.jpg', img_data.getvalue(), content_type='image/jpeg')
        
        self.image = Image.objects.create(
            user=self.user,
            original_image=uploaded_file
        )
    
    def test_temporary_link_creation(self):
        """Test temporary link creation and expiration calculation."""
        expires_in = 3600  # 1 hour
        
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=expires_in
        )
        
        self.assertIsNotNone(temp_link.expires_at)
        self.assertFalse(temp_link.is_used)
        self.assertTrue(temp_link.is_valid())
        self.assertFalse(temp_link.is_expired())
    
    def test_temporary_link_expiration(self):
        """Test temporary link expiration."""
        # Create expired link
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=300,
            expires_at=timezone.now() - timedelta(minutes=1)  # Expired 1 minute ago
        )
        
        self.assertTrue(temp_link.is_expired())
        self.assertFalse(temp_link.is_valid())
    
    def test_temporary_link_mark_as_used(self):
        """Test marking temporary link as used."""
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=3600
        )
        
        # Mark as used
        temp_link.mark_as_used()
        
        self.assertTrue(temp_link.is_used)
        self.assertIsNotNone(temp_link.used_at)
        self.assertFalse(temp_link.is_valid())
