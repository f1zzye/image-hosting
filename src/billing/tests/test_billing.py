from http import HTTPStatus
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from billing.models import TariffPlan, UserTariff


def create_user(
    email="user@example.com", username="testuser", password="TestPassword123!"
):
    user = get_user_model().objects.create_user(
        email=email, username=username, password=password
    )
    user.is_active = True
    user.save()
    return user


class TestUpgradeTariffView(TransactionTestCase):
    fixtures = ["billing/fixtures/default_plans.json"]

    path_name: str = "billing:update_tariff"
    template_name: str = "billing/upgrade_tariff.html"
    title: str = "Upgrade Tariff"

    def setUp(self):
        self.client = Client()
        self.user = create_user()

        self.basic_plan = TariffPlan.objects.get(title="Basic")
        self.premium_plan = TariffPlan.objects.get(title="Premium")
        self.enterprise_plan = TariffPlan.objects.get(title="Enterprise")

        self.user_tariff, created = UserTariff.objects.get_or_create(
            user=self.user,
            defaults={
                "plan": self.basic_plan,
                "is_active": True,
                "expires_at": None,
                "paypal_subscription_id": "old_subscription_id",
            },
        )

        if not created:
            self.user_tariff.plan = self.basic_plan
            self.user_tariff.is_active = True
            self.user_tariff.expires_at = None
            self.user_tariff.paypal_subscription_id = "old_subscription_id"
            self.user_tariff.expiration_notification_sent = False
            self.user_tariff.save()

    def test_upgrade_tariff_requires_login(self):
        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": "test_subscription_id", "new_plan": "Premium"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f"/user/sign-in/?next={url}")

    def test_upgrade_to_premium_success(self):
        self.client.force_login(self.user)

        tariff_id = "new_premium_subscription_id"
        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": tariff_id, "new_plan": "Premium"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "billing/upgrade_tariff.html")
        self.assertEqual(response.context["title"], "Upgrade Tariff")
        self.assertEqual(response.context["tariff_plan"], self.premium_plan)

        self.user_tariff.refresh_from_db()
        self.assertEqual(self.user_tariff.plan, self.premium_plan)
        self.assertEqual(self.user_tariff.paypal_subscription_id, tariff_id)
        self.assertIsNotNone(self.user_tariff.expires_at)
        self.assertFalse(self.user_tariff.expiration_notification_sent)

        expected_expires_at = timezone.now() + timedelta(days=30)
        self.assertAlmostEqual(
            self.user_tariff.expires_at.timestamp(),
            expected_expires_at.timestamp(),
            delta=60,
        )

    def test_upgrade_to_enterprise_success(self):
        self.client.force_login(self.user)

        tariff_id = "new_enterprise_subscription_id"
        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": tariff_id, "new_plan": "Enterprise"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["tariff_plan"], self.enterprise_plan)

        self.user_tariff.refresh_from_db()
        self.assertEqual(self.user_tariff.plan, self.enterprise_plan)
        self.assertEqual(self.user_tariff.paypal_subscription_id, tariff_id)
        self.assertIsNotNone(self.user_tariff.expires_at)
        self.assertFalse(self.user_tariff.expiration_notification_sent)

    def test_downgrade_to_basic_success(self):
        self.user_tariff.plan = self.premium_plan
        self.user_tariff.expires_at = timezone.now() + timedelta(days=15)
        self.user_tariff.expiration_notification_sent = True
        self.user_tariff.save()

        self.client.force_login(self.user)

        tariff_id = "basic_subscription_id"
        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": tariff_id, "new_plan": "Basic"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["tariff_plan"], self.basic_plan)

        self.user_tariff.refresh_from_db()
        self.assertEqual(self.user_tariff.plan, self.basic_plan)
        self.assertEqual(self.user_tariff.paypal_subscription_id, tariff_id)
        self.assertIsNone(self.user_tariff.expires_at)
        self.assertFalse(self.user_tariff.expiration_notification_sent)

    def test_upgrade_tariff_nonexistent_user_tariff(self):
        user_without_tariff = create_user(
            email="no_tariff@example.com", username="no_tariff_user"
        )
        UserTariff.objects.filter(user=user_without_tariff).delete()

        self.client.force_login(user_without_tariff)

        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": "test_id", "new_plan": "Premium"},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_upgrade_tariff_nonexistent_plan(self):
        self.client.force_login(self.user)

        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": "test_id", "new_plan": "NonexistentPlan"},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_upgrade_tariff_inactive_user_tariff(self):
        self.user_tariff.is_active = False
        self.user_tariff.save()

        other_user = create_user(email="other@example.com", username="other_user")
        UserTariff.objects.get_or_create(
            user=other_user, defaults={"plan": self.premium_plan, "is_active": True}
        )

        self.client.force_login(self.user)

        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": "test_id", "new_plan": "Premium"},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_upgrade_tariff_resets_expiration_notification_flag(self):
        self.user_tariff.expiration_notification_sent = True
        self.user_tariff.save()

        self.client.force_login(self.user)

        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": "test_subscription_id", "new_plan": "Premium"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.user_tariff.refresh_from_db()
        self.assertFalse(self.user_tariff.expiration_notification_sent)

    def test_upgrade_from_premium_to_enterprise(self):
        self.user_tariff.plan = self.premium_plan
        self.user_tariff.expires_at = timezone.now() + timedelta(days=10)
        self.user_tariff.save()

        self.client.force_login(self.user)

        tariff_id = "enterprise_subscription_id"
        url = reverse(
            "billing:update_tariff",
            kwargs={"tariff_id": tariff_id, "new_plan": "Enterprise"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["tariff_plan"], self.enterprise_plan)

        self.user_tariff.refresh_from_db()
        self.assertEqual(self.user_tariff.plan, self.enterprise_plan)
        self.assertEqual(self.user_tariff.paypal_subscription_id, tariff_id)

        expected_expires_at = timezone.now() + timedelta(days=30)
        self.assertAlmostEqual(
            self.user_tariff.expires_at.timestamp(),
            expected_expires_at.timestamp(),
            delta=60,
        )
