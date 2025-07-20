from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from accounts.tests.common_test import CommonTest


class TestRegistrationUser(CommonTest):
    path_name: str = "accounts:sign-up"
    template_name: str = "accounts/sign-up.html"
    title: str = "Sign Up - PhotoHub"

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.valid_data = {
            "email": "example@gmail.com",
            "username": "exampleuser",
            "password1": "ExamplePassword123!",
            "password2": "ExamplePassword123!",
        }

    def test_common(self):
        self.common_test()

    def test_user_registration_post_success(self):
        email = self.valid_data["email"]
        self.assertFalse(get_user_model().objects.filter(email=email).exists())
        response = self.client.post(self.path, self.valid_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("core:index"))
        self.assertTrue(get_user_model().objects.filter(email=email).exists())
        user = get_user_model().objects.get(email=email)
        self.assertFalse(user.is_active)

    def test_user_registration_post_invalid_data(self):
        invalid_data = {
            "email": "invalid-email",
            "username": "exampleuser",
            "password1": "ExamplePassword123!",
            "password2": "DifferentPassword123!",
        }

        response = self.client.post(self.path, invalid_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertFalse(get_user_model().objects.filter(email=invalid_data["email"]).exists())
        self.assertContains(response, "Enter a valid email address")

    def test_user_registration_duplicate_email(self):
        get_user_model().objects.create_user(
            email=self.valid_data["email"],
            username="existing_user",
            password="password123"
        )

        response = self.client.post(self.path, self.valid_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(get_user_model().objects.filter(email=self.valid_data["email"]).count(), 1)

