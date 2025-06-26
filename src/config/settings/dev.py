from config.settings.base import *  # noqa
from decouple import config

DEBUG = True

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["*", "127.0.0.1", "localhost"]

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