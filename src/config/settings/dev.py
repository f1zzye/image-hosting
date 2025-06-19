from config.settings.base import *  # noqa

DEBUG = True

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["*", "127.0.0.1", "localhost"]

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

STATIC_ROOT = BASE_DIR / "staticfiles"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
