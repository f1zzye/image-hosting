#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_DIR = BASE_DIR / "LOGS"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "errors.log"

logger.remove()
logger.add(
    str(LOG_FILE),
    level="ERROR",
    rotation="10 MB",
    retention="10 days",
)
logger.add(sys.stderr, level="ERROR")


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
