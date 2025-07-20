from http import HTTPStatus

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from accounts.tests.common_test import CommonTest


def create_user(email="user@example.com", username="testuser", password="TestPassword123!"):
    user = get_user_model().objects.create_user(email=email, username=username, password=password)
    user.is_active = True
    user.save()
    return user


def create_admin_user(email="admin@example.com", username="admin", password="TestPassword123!", is_superuser=True):
    user = get_user_model().objects.create_superuser(
        email=email,
        username=username,
        password=password,
        is_superuser=is_superuser
    )
    user.is_active = True
    user.save()
    return user


class TestAuthUser(CommonTest):
    path_name: str = "accounts:sign-in"
    template_name: str = "accounts/sign-in.html"
    title: str = "Sign In - PhotoHub"

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = create_user()
        self.admin_user = create_admin_user()

    def test_common(self):
        self.common_test()

    def test_login_with_invalid_email(self):
        response = self.client.post(
            self.path, {"email": "user@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_login_with_valid_email(self):
        response = self.client.post(
            self.path, {"email": "user@example.com", "password": "TestPassword123!"}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_access_admin_panel(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_admin_access_admin_panel(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)