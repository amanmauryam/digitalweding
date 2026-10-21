"""WSGI config for the DigitalWedding project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digitalwedding.settings")

application = get_wsgi_application()
