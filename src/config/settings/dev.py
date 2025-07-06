import os

from config.settings.base import *  # noqa
from decouple import config

DEBUG = True

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"  # noqa

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa
    }
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

SITE_URL = "127.0.0.1:8000"

PAYPAL_URL = os.environ.get("PAYPAL_URL")

PREMIUM_TARIFF_ID = config('PREMIUM_TARIFF_ID')
ENTERPRISE_TARIFF_ID = config('ENTERPRISE_TARIFF_ID')