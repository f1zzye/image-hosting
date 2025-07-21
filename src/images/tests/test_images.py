import json
import uuid
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from images.models import Image, TemporaryLink
from accounts.tests.common_test import CommonTest

User = get_user_model()


def create_user(
    email="user@example.com", username="testuser", password="TestPassword123!"
):
    user = get_user_model().objects.create_user(
        email=email, username=username, password=password
    )
    user.is_active = True
    user.save()
    return user


class TestDeleteImageView(CommonTest):
    path_name: str = "images:delete-image"
    template_name: str = None
    title: str = None

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = create_user()
        self.other_user = create_user(
            email="other@example.com", username="otheruser", password="TestPassword123!"
        )

        test_image = SimpleUploadedFile(
            "test.jpg", b"fake_image_content", content_type="image/jpeg"
        )

        self.image = Image.objects.create(
            user=self.user,
            original_image=test_image,
        )

        self.other_user_image = Image.objects.create(
            user=self.other_user,
            original_image=test_image,
        )

        self.delete_url = reverse("images:delete-image")

    def test_delete_image_requires_login(self):
        response = self.client.post(self.delete_url, {"image_id": self.image.id})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f"/user/sign-in/?next={self.delete_url}")

    def test_delete_image_success(self):
        self.client.force_login(self.user)

        self.assertTrue(Image.objects.filter(id=self.image.id).exists())

        response = self.client.post(self.delete_url, {"image_id": self.image.id})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"success": True})
        self.assertFalse(Image.objects.filter(id=self.image.id).exists())

    def test_delete_image_missing_image_id(self):
        self.client.force_login(self.user)

        response = self.client.post(self.delete_url, {})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Image ID is required"})

    def test_delete_image_nonexistent_image(self):
        self.client.force_login(self.user)
        fake_uuid = uuid.uuid4()
        response = self.client.post(self.delete_url, {"image_id": fake_uuid})

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestCreateTemporaryLinkView(CommonTest):
    path_name: str = "images:create-temporary-link"
    template_name: str = None
    title: str = None

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = create_user()
        self.other_user = create_user(
            email="other@example.com", username="otheruser", password="TestPassword123!"
        )

        test_image = SimpleUploadedFile(
            "test.jpg", b"fake_image_content", content_type="image/jpeg"
        )

        self.image = Image.objects.create(
            user=self.user,
            original_image=test_image,
        )

        self.other_user_image = Image.objects.create(
            user=self.other_user,
            original_image=test_image,
        )

        self.create_link_url = reverse("images:create-temporary-link")

    def test_create_temporary_link_requires_login(self):
        data = {"image_id": str(self.image.id)}
        response = self.client.post(
            self.create_link_url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f"/user/sign-in/?next={self.create_link_url}")

    def test_create_temporary_link_success(self):
        self.client.force_login(self.user)

        data = {"image_id": str(self.image.id)}
        response = self.client.post(
            self.create_link_url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = response.json()

        self.assertTrue(response_data["success"])
        self.assertIn("link_url", response_data)
        self.assertIn("expires_at", response_data)
        self.assertEqual(response_data["expires_in_seconds"], 3600)

        temp_link = TemporaryLink.objects.get(image=self.image, user=self.user)
        self.assertIsNotNone(temp_link)
        self.assertEqual(temp_link.expires_in_seconds, 3600)

    def test_create_temporary_link_invalid_json(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_link_url, "invalid json", content_type="application/json"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["error"], "Invalid JSON")


class TestTemporaryLinkView(CommonTest):
    path_name: str = None
    template_name: str = None
    title: str = None

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = create_user()

        test_image = SimpleUploadedFile(
            "test.jpg", b"fake_image_content", content_type="image/jpeg"
        )

        self.image = Image.objects.create(
            user=self.user,
            original_image=test_image,
        )

    def test_temporary_link_view_success(self):
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=3600,
        )

        url = reverse("images:temporary_link_view", kwargs={"link_id": temp_link.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertEqual(response.content, b"fake_image_content")

    def test_temporary_link_view_nonexistent_link(self):
        fake_uuid = uuid.uuid4()
        url = reverse("images:temporary_link_view", kwargs={"link_id": fake_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch.object(TemporaryLink, "is_valid")
    def test_temporary_link_view_expired_link(self, mock_is_valid):
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=3600,
        )

        mock_is_valid.return_value = False

        url = reverse("images:temporary_link_view", kwargs={"link_id": temp_link.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch.object(TemporaryLink, "is_valid")
    def test_temporary_link_view_invalid_link(self, mock_is_valid):
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=3600,
        )

        mock_is_valid.return_value = False

        url = reverse("images:temporary_link_view", kwargs={"link_id": temp_link.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_temporary_link_view_no_authentication_required(self):
        temp_link = TemporaryLink.objects.create(
            image=self.image,
            user=self.user,
            expires_in_seconds=3600,
        )

        url = reverse("images:temporary_link_view", kwargs={"link_id": temp_link.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Type"], "image/jpeg")
