from config.settings.base import *  # noqa
from celery.schedules import crontab

DEBUG = False

SECRET_KEY = "django-secret-key"

ALLOWED_HOSTS = ["localhost"]

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa
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
