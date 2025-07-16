import os
from pathlib import Path
from config.settings.base import *  # noqa
from celery.schedules import crontab
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = False

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


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
        "schedule": crontab(minute=0, hour="*/1"),  # Каждый час: 00:00, 01:00, 02:00...
    },
    "check-expiring-subscriptions": {
        "task": "billing.tasks.check_expiring_subscriptions",
        "schedule": crontab(minute=0, hour=[9, 18]),  # Каждый день в 09:00, 18 UTC
    },
}
