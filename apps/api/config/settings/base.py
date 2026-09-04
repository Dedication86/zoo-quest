"""
Zoo Quest API - base settings shared by every environment.

Environment-specific values come from environment variables (see .env.example).
Never put secrets or hostnames in this file.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # apps/api/

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-only-insecure-key-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---------------------------------------------------------------- apps
DJANGO_APPS = [
    "unfold",  # admin theme; must precede django.contrib.admin
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
]
LOCAL_APPS = [
    "apps.tenants",  # zoos and staff membership (the tenant layer)
    "apps.content",  # what a zoo authors: exhibits, animals, markers, challenges, quests, badges
    "apps.play",  # what a family does: sessions, scans, discoveries, progress, XP
    "apps.analytics",  # engagement events
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------- database
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://zooquest:zooquest@localhost:5432/zooquest"),
}
DATABASES["default"]["CONN_MAX_AGE"] = 60
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------- auth
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------- i18n
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"  # each Zoo carries its own timezone for display
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------- static & media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------- CORS / CSRF
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-guest-token",  # explorer session token (see Blueprint, Section E)
]

# ---------------------------------------------------------------- DRF
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "120/min", "scan": "30/min", "submit": "30/min"},
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Zoo Quest API",
    "DESCRIPTION": "Turn a day at the zoo into an adventure.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------- Zoo Quest
# Public URL of the explorer app. Printed QR codes encode PLAY_BASE_URL + /s/<code>.
PLAY_BASE_URL = env("PLAY_BASE_URL", default="http://localhost:3000").rstrip("/")

# ---------------------------------------------------------------- Zoo Quest game defaults
# Per-zoo overrides live in Zoo.settings (JSON). These are only the fallbacks
# used when a zoo has not configured a value. Nothing in game code should
# reference a literal XP number; it should call the settings helper (M1).
ZOOQUEST_DEFAULTS = {
    "discovery_xp": 100,
    "quest_complete_xp": 500,
    "xp_by_difficulty": {"easy": 50, "medium": 100, "hard": 250},
    "repeat_scan_cooldown_minutes": 1440,
}

# ---------------------------------------------------------------- admin (Unfold)
UNFOLD = {
    "SITE_TITLE": "Zoo Quest",
    "SITE_HEADER": "Zoo Quest",
    "SITE_SUBHEADER": "Manage your zoo",
    "SITE_SYMBOL": "pets",
    "SHOW_HISTORY": True,
    "COLORS": {
        "primary": {
            "50": "236 245 239",
            "100": "215 235 222",
            "200": "176 214 191",
            "300": "133 190 155",
            "400": "95 163 122",
            "500": "63 138 99",
            "600": "47 107 79",
            "700": "38 86 64",
            "800": "30 68 51",
            "900": "22 50 38",
            "950": "11 26 20",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": "Zoo",
                "items": [
                    {"title": "Zoos", "icon": "park", "link": "/admin/tenants/zoo/"},
                    {"title": "Staff", "icon": "badge", "link": "/admin/tenants/staffmembership/"},
                    {"title": "Levels", "icon": "trending_up", "link": "/admin/content/level/"},
                ],
            },
            {
                "title": "Content",
                "items": [
                    {"title": "Exhibits", "icon": "map", "link": "/admin/content/exhibit/"},
                    {"title": "Animals", "icon": "pets", "link": "/admin/content/animal/"},
                    {"title": "QR Markers", "icon": "qr_code_2", "link": "/admin/content/marker/"},
                    {"title": "Challenges", "icon": "flag", "link": "/admin/content/challenge/"},
                    {"title": "Quests", "icon": "explore", "link": "/admin/content/quest/"},
                    {"title": "Badges", "icon": "military_tech", "link": "/admin/content/badge/"},
                ],
            },
        ],
    },
}
