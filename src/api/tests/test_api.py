from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

from images.models import Image
from billing.models import TariffPlan, UserTariff
from api.views import ImagesViewSet, TariffPlanView, UserTariffView


def create_user(
    email="user@example.com", username="testuser", password="TestPassword123!"
):
    user = get_user_model().objects.create_user(
        email=email, username=username, password=password
    )
    user.is_active = True
    user.save()
    return user


def create_admin_user(
    email="admin@example.com",
    username="admin",
    password="TestPassword123!",
    is_superuser=True,
):
    user = get_user_model().objects.create_superuser(
        email=email, username=username, password=password, is_superuser=is_superuser
    )
    user.is_active = True
    user.save()
    return user


def create_test_tariff_plan(
    title="Premium",
    description="Premium Plan",
    price=Decimal("9.99"),
    has_thumbnail_200px=True,
    has_thumbnail_400px=True,
    has_original_photo=True,
    has_binary_link=False,
):
    return TariffPlan.objects.create(
        title=title,
        description=description,
        price=price,
        has_thumbnail_200px=has_thumbnail_200px,
        has_thumbnail_400px=has_thumbnail_400px,
        has_original_photo=has_original_photo,
        has_binary_link=has_binary_link,
    )


def create_user_tariff(user, plan, is_active=True):
    return UserTariff.objects.create(
        user=user,
        plan=plan,
        is_active=is_active,
    )


def create_test_image(user, file_name="test.jpg"):
    file = SimpleUploadedFile(
        file_name, b"fake_image_content", content_type="image/jpeg"
    )
    return Image.objects.create(
        user=user,
        original_image=file,
    )


class APITests(APITestCase):
    def setUp(self):
        self.user = create_user(email="user@example.com")
        self.admin = create_admin_user(email="admin@example.com")

        response = self.client.post(
            reverse("api:token_obtain_pair"),
            {"email": "user@example.com", "password": "TestPassword123!"},
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Failed to obtain user token"
        )
        self.token = response.data["access"]

        response = self.client.post(
            reverse("api:token_obtain_pair"),
            {"email": "admin@example.com", "password": "TestPassword123!"},
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Failed to obtain admin token"
        )
        self.admin_token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.plan = create_test_tariff_plan()
        self.subscription = create_user_tariff(self.user, self.plan)
        self.image = create_test_image(self.user)

    def test_images_viewset(self):
        list_url = reverse("api:images-list")
        detail_url = reverse("api:images-detail", kwargs={"pk": self.image.pk})

        self.client.credentials()
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["id"]), str(self.image.pk))

        search_url = f"{list_url}?search=test"
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ordering_url = f"{list_url}?ordering=-created_at"
        response = self.client.get(ordering_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            list_url,
            {
                "original_image": SimpleUploadedFile(
                    "test.jpg", b"fake_image_content", content_type="image/jpeg"
                )
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(
            detail_url,
            {
                "original_image": SimpleUploadedFile(
                    "test.jpg", b"fake_image_content", content_type="image/jpeg"
                )
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with patch.object(
            ImagesViewSet, "get_queryset", side_effect=Exception("Database error")
        ):
            response = self.client.get(list_url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertEqual(response.data["detail"], "Internal server error.")

        with patch.object(
            ImagesViewSet, "get_object", side_effect=Exception("Database error")
        ):
            response = self.client.get(detail_url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertEqual(response.data["detail"], "Internal server error.")

    def test_tariffs_viewset(self):
        list_url = reverse("api:tariffs-list")
        detail_url = reverse("api:tariffs-detail", kwargs={"pk": self.plan.pk})

        self.client.credentials()
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.plan.title)

        search_url = f"{list_url}?search={self.plan.title}"
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        ordering_url = f"{list_url}?ordering=price"
        response = self.client.get(ordering_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            list_url,
            {"title": "New Plan", "description": "New", "price": "19.99"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(detail_url, {"title": "Updated Plan"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        response = self.client.post(
            list_url,
            {"title": "Admin Plan", "description": "Admin", "price": "29.99"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(
            detail_url,
            {
                "title": "Updated Admin Plan",
                "description": self.plan.description,
                "price": str(self.plan.price),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        UserTariff.objects.filter(plan=self.plan).delete()

        response = self.client.delete(detail_url)
        self.assertIn(
            response.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK)
        )

        with patch.object(
            TariffPlanView, "get_queryset", side_effect=Exception("Database error")
        ):
            response = self.client.get(list_url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertEqual(response.data["detail"], "Internal server error.")

        with patch.object(
            TariffPlanView, "get_object", side_effect=Exception("Database error")
        ):
            response = self.client.get(detail_url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertEqual(response.data["detail"], "Internal server error.")

    def test_user_tariffs_viewset(self):
        list_url = reverse("api:user-tariffs-list")
        detail_url = reverse(
            "api:user-tariffs-detail", kwargs={"pk": self.subscription.pk}
        )

        self.client.credentials()
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)

        search_url = f"{list_url}?search={self.user.username}"
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

        ordering_url = f"{list_url}?ordering=-created_at"
        response = self.client.get(ordering_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            list_url, {"user": self.user.id, "plan": self.plan.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with patch.object(
            UserTariffView, "get_queryset", side_effect=Exception("Database error")
        ):
            response = self.client.get(list_url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertEqual(response.data["detail"], "Internal server error.")

        with patch.object(
            UserTariffView, "get_object", side_effect=Exception("Database error")
        ):
            response = self.client.get(detail_url)
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.assertEqual(response.data["detail"], "Internal server error.")

    def test_health_check(self):
        response = self.client.get(reverse("api:health"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("version", response.data)
        self.assertIn("dependencies", response.data)
        self.assertIn("timestamp", response.data)

    def test_token_endpoints(self):
        response = self.client.post(
            reverse("api:token_obtain_pair"),
            {"email": "user@example.com", "password": "TestPassword123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_token = response.data["refresh"]
        response = self.client.post(
            reverse("api:token_refresh"), {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        access_token = response.data["access"]
        response = self.client.post(
            reverse("api:token_verify"), {"token": access_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
