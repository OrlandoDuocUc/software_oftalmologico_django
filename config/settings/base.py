"""
Base settings for the OFTALMETRYC DJANGO project.

This module centralises every configuration shared by local, staging
and production environments. Environment-specific overrides live in
config/settings/local.py or config/settings/production.py.
"""

from pathlib import Path
import os
import sys
from datetime import timedelta

import dj_database_url
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths & Environment helpers
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# Ensure the custom apps folder is importable
if APPS_DIR.exists():
    sys.path.insert(0, str(APPS_DIR))

# Load .env values (keeps compatibility with the Flask project)
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Core Django configuration
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"

# Nota: el valor por defecto incluye el dominio de Render para evitar errores
# cuando no se dispone de variables de entorno (solo útil en entornos de prueba).
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost,oftalmetryc-django.onrender.com",
    ).split(",")
    if host.strip()
]

# Base apps separation keeps things tidy when the project grows
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.inventory.apps.InventoryConfig",
    "apps.clients.apps.ClientsConfig",
    "apps.sales.apps.SalesConfig",
    "apps.medical.apps.MedicalConfig",
    "apps.shared.apps.SharedConfig",
    "apps.api.apps.ApiConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "core.context_processors.global_settings",
            ],
            "builtins": [
                "apps.core.templatetags.currency_filters",
                "apps.core.templatetags.json_filters",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=os.getenv("DATABASE_SSL_REQUIRE", "false").lower() == "true",
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "auth.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "apps.accounts.backends.LegacyUserBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "user_html:login"
LOGIN_REDIRECT_URL = "routes:home"
LOGOUT_REDIRECT_URL = "user_html:login"

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es-cl"
TIME_ZONE = os.getenv("TIME_ZONE", "America/Santiago")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# REST & API defaults (DRF mirrors existing Flask API behaviour)
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

# Simple flag to know when we are running under tests
IS_TESTING = os.getenv("PYTEST_CURRENT_TEST") is not None
