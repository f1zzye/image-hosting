from http import HTTPStatus
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from images.models import Image
from images.forms import ImageUploadForm
from billing.models import TariffPlan, UserTariff
from accounts.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages

User = get_user_model()


def create_user(
    email="user@example.com", username="testuser", password="TestPassword123!"
):
    user = User.objects.create_user(email=email, username=username, password=password)
    user.is_active = True
    user.save()
    return user


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.basic_plan, _ = TariffPlan.objects.get_or_create(
            title="Basic",
            defaults={
                "description": "Perfect for personal use and small projects.",
                "price": 0.00,
                "is_built_in": True,
                "has_thumbnail_200px": True,
                "has_thumbnail_400px": False,
                "has_original_photo": False,
                "has_binary_link": False,
            },
        )
        self.user = create_user()
        self.premium_plan, _ = TariffPlan.objects.get_or_create(
            title="Premium",
            defaults={
                "description": "Designed for content creators and small businesses.",
                "price": 24.99,
                "is_built_in": True,
                "has_thumbnail_200px": True,
                "has_thumbnail_400px": True,
                "has_original_photo": True,
                "has_binary_link": False,
            },
        )
        self.enterprise_plan, _ = TariffPlan.objects.get_or_create(
            title="Enterprise",
            defaults={
                "description": "Ultimate solution for agencies, large businesses, and power users.",
                "price": 39.99,
                "is_built_in": True,
                "has_thumbnail_200px": True,
                "has_thumbnail_400px": True,
                "has_original_photo": True,
                "has_binary_link": True,
            },
        )
        self.user_tariff, _ = UserTariff.objects.get_or_create(
            user=self.user, defaults={"plan": self.basic_plan, "is_active": True}
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)

    def test_index_view_get(self):
        url = reverse("core:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "index.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ImageUploadForm)
        self.assertEqual(response.context["title"], "PhotoHub - Premium Photo Hosting")

    def test_index_view_post_requires_auth(self):
        url = reverse("core:index")
        response = self.client.post(url, {"file": ""})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("accounts:sign-in"))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages_list[0]),
            "Please sign in or create an account to upload photos.",
        )

    # def test_index_view_post_authenticated_upload(self):
    #     self.client.force_login(self.user)
    #     url = reverse("core:index")
    #     test_image = SimpleUploadedFile(
    #         "test.jpg", b"fake_image_content", content_type="image/jpeg"
    #     )
    #     response = self.client.post(url, {"original_image": test_image}, format="multipart")
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertRedirects(response, reverse("core:profile"))
    #     self.assertEqual(Image.objects.filter(user=self.user).count(), 1)

    def test_tariff_plans_view_requires_login(self):
        url = reverse("core:pricing")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("/user/sign-in", response.url)

    def test_tariff_plans_view_authenticated(self):
        self.client.force_login(self.user)
        url = reverse("core:pricing")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "core/pricing.html")
        self.assertIn("plans", response.context)

    def test_profile_view_requires_login(self):
        url = reverse("core:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("/user/sign-in", response.url)

    def test_profile_view_authenticated(self):
        self.client.force_login(self.user)
        url = reverse("core:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "core/profile.html")
        self.assertIn("user_profile", response.context)
        self.assertIn("days_left", response.context)

    def test_image_download_permission_check_authenticated(self):
        self.client.force_login(self.user)
        file = SimpleUploadedFile(
            "test.jpg", b"fake_image_content", content_type="image/jpeg"
        )
        image = Image.objects.create(user=self.user, original_image=file)
        url = reverse("core:download_permissions", args=[image.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("image_id", response.json())

    def test_contact_us_view_get(self):
        url = reverse("core:contacts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "core/contacts.html")

    def test_ajax_contact_view(self):
        url = reverse("core:ajax-contact-form")
        response = self.client.get(
            url,
            {
                "full_name": "Test User",
                "email": "test@example.com",
                "message": "Test!",
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("context", response.json())
        self.assertTrue(response.json()["context"]["bool"])
