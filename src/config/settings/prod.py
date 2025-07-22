import os
from pathlib import Path
from config.settings.base import *  # noqa
from celery.schedules import crontab
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = False

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

STATIC_ROOT = BASE_DIR / "staticfiles"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

CELERY_BEAT_SCHEDULE = {
    "process-expired-tariffs": {
        "task": "billing.tasks.process_expired_tariffs",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "check-expiring-subscriptions": {
        "task": "billing.tasks.check_expiring_subscriptions",
        "schedule": crontab(minute=0, hour=[9, 18]),
    },
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_FAIL_SILENTLY = False


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

SOCIAL_AUTH_GITHUB_KEY = config("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = config("SOCIAL_AUTH_GITHUB_SECRET")

SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]

SOCIAL_AUTH_GITHUB_EXTRA_DATA = ["login", "name"]

SOCIAL_AUTH_USER_FIELDS = ["username", "email", "first_name", "last_name"]

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_SECRET_ID = os.environ.get("PAYPAL_SECRET_ID")

PAYPAL_URL = os.environ.get("PAYPAL_URL")

PREMIUM_TARIFF_ID = config("PREMIUM_TARIFF_ID")
ENTERPRISE_TARIFF_ID = config("ENTERPRISE_TARIFF_ID")

SITE_URL = "localhost:8000"