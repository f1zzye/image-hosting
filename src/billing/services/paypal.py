import json
import logging
import os

from http import HTTPStatus
from typing import Dict, Optional

import requests

from billing.models import TariffPlan, UserTariff


def get_access_token():
    data = {
        "grant_type": "client_credentials",
    }

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }

    client_id = os.environ.get("PAYPAL_CLIENT_ID")
    client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
    paypal_url = os.environ.get("PAYPAL_URL")

    if not all([client_id, client_secret, paypal_url]):
        logging.error("Missing PayPal credentials in environment variables")
        return None

    paypal_base_url = f"{paypal_url}/v1/oauth2/token"

    try:
        response = requests.post(
            paypal_base_url,
            data=data,
            headers=headers,
            auth=(client_id, client_secret),
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        logging.error(f"Error obtaining access token: {e}")
        return None


def get_paypal_headers(access_token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }


def get_current_tariff(access_token, tariff_id):
    url = f'{os.environ.get("PAYPAL_URL")}/v1/billing/plans/{tariff_id}'

    try:
        response = requests.get(
            url,
            headers=get_paypal_headers(access_token),
        )

        if response.status_code == HTTPStatus.OK:
            plan_data = response.json()
            logging.info(f"Retrieved tariff data for plan: {tariff_id}")
            return plan_data

        elif response.status_code == HTTPStatus.NOT_FOUND:
            logging.error(f"Tariff plan not found: {tariff_id}")
            return None

        else:
            logging.error(f"PayPal API error: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        logging.error(f"Error retrieving tariff data: {e}")
        return None


def cancel_subscription(access_token, subscription_id, reason="User requested cancellation"):
    url = f'{os.environ.get("PAYPAL_URL")}/v1/billing/subscriptions/{subscription_id}/cancel'

    data = {"reason": reason}

    try:
        response = requests.post(
            url,
            headers=get_paypal_headers(access_token),
            json=data,
        )

        if response.status_code == HTTPStatus.NO_CONTENT:
            logging.info(f"Successfully canceled subscription: {subscription_id}")
            return True

        elif response.status_code == HTTPStatus.NOT_FOUND:
            logging.error(f"Subscription not found: {subscription_id}")
            return False

        else:
            logging.error(f"PayPal API error: {response.status_code} - {response.text}")
            return False

    except requests.RequestException as e:
        logging.error(f"Error canceling subscription: {e}")
        return False


import os
from http import HTTPStatus
from typing import Dict
import json  # ← ДОБАВЬ ЭТОТ ИМПОРТ!

import requests
import logging

from src.billing.models import UserTariff, TariffPlan


def get_access_token():
    data = {
        "grant_type": "client_credentials",
    }

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }

    client_id = os.environ.get("PAYPAL_CLIENT_ID")
    client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
    paypal_url = os.environ.get("PAYPAL_URL")

    if not all([client_id, client_secret, paypal_url]):
        logging.error("Missing PayPal credentials in environment variables")
        return None

    paypal_base_url = f"{paypal_url}/v1/oauth2/token"

    try:
        response = requests.post(
            paypal_base_url,
            data=data,
            headers=headers,
            auth=(client_id, client_secret),
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        logging.error(f"Error obtaining access token: {e}")
        return None


def get_paypal_headers(access_token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }


def get_current_tariff(access_token, tariff_id):
    url = f'{os.environ.get("PAYPAL_URL")}/v1/billing/plans/{tariff_id}'

    try:
        response = requests.get(
            url, headers=get_paypal_headers(access_token), timeout=30
        )

        if response.status_code == HTTPStatus.OK:
            plan_data = response.json()
            logging.info(f"Retrieved tariff data for plan: {tariff_id}")
            return plan_data

        elif response.status_code == HTTPStatus.NOT_FOUND:
            logging.error(f"Tariff plan not found: {tariff_id}")
            return None

        else:
            logging.error(f"PayPal API error: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        logging.error(f"Error retrieving tariff data: {e}")
        return None


def cancel_subscription(access_token, subscription_id, reason="User requested cancellation"):
    url = f'{os.environ.get("PAYPAL_URL")}/v1/billing/subscriptions/{subscription_id}/cancel'

    data = {"reason": reason}

    try:
        response = requests.post(
            url, headers=get_paypal_headers(access_token), json=data, timeout=30
        )

        if response.status_code == HTTPStatus.NO_CONTENT:
            logging.info(f"Successfully canceled subscription: {subscription_id}")
            return True

        elif response.status_code == HTTPStatus.NOT_FOUND:
            logging.error(f"Subscription not found: {subscription_id}")
            return False

        else:
            logging.error(f"PayPal API error: {response.status_code} - {response.text}")
            return False

    except requests.RequestException as e:
        logging.error(f"Error canceling subscription: {e}")
        return False


def update_subscription_paypal(access_token, subscription_id: str, new_plan: str):

    try:
        user_subscription = UserTariff.objects.select_related("plan").get(
            paypal_subscription_id=subscription_id
        )
        current_plan = user_subscription.plan.title

        new_subscription_plan = TariffPlan.objects.get(title=new_plan)
        new_subscription_plan_id = new_subscription_plan.paypal_plan_id

        if not new_subscription_plan_id:
            logging.error(f"New tariff plan '{new_plan}' has no PayPal plan_id")
            return None

        url: str = (
            f'{os.environ.get("PAYPAL_URL")}/v1/billing/subscriptions/{subscription_id}/revise'
        )

        revision_data: Dict[str, str] = {
            "plan_id": new_subscription_plan_id,
        }

        response = requests.post(
            url,
            headers=get_paypal_headers(access_token),
            json=revision_data,
            timeout=30,
        )

        if response.status_code == HTTPStatus.OK:
            response_data = response.json()

            for link in response_data.get("links", []):
                if link.get("rel") == "approve":
                    approve_link = link.get("href")
                    logging.info(
                        f"Successfully initiated subscription update: {subscription_id} from {current_plan} to {new_plan}"
                    )
                    return approve_link

            logging.error(
                f"No approve link found in PayPal response for subscription: {subscription_id}"
            )
            return None

        elif response.status_code == HTTPStatus.NOT_FOUND:
            logging.error(f"Subscription not found: {subscription_id}")
            return None

        else:
            logging.error(f"PayPal API error: {response.status_code} - {response.text}")
            return None

    except (UserTariff.DoesNotExist, TariffPlan.DoesNotExist) as e:
        logging.error(f"Error updating subscription: {e}")
        return None
