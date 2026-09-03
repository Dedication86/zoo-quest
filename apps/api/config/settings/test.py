"""Settings for the test suite. Uses the same Postgres as local unless DATABASE_URL says otherwise."""

from .local import *  # noqa: F401,F403
from .local import REST_FRAMEWORK

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
