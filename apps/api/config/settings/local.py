"""Local development settings."""

from .base import *  # noqa: F401,F403
from .base import CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS, REST_FRAMEWORK, STORAGES

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"]
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"]

# Plain static storage locally so `collectstatic` is never required to run the dev server.
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

# Browsable API is handy while developing.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Serve static files straight from app directories in development.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
