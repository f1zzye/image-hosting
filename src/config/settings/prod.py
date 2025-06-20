from config.settings.base import *  # noqa

DEBUG = False

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["localhost"]

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles" # noqa

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media" # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3", # noqa
    }
}
