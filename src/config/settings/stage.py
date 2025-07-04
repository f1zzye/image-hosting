from config.settings.base import *  # noqa

DEBUG = False

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["*"]

STATIC_URL = "/static/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa
    }
}
