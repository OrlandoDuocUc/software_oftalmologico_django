"""
Local settings module.

Extends the base configuration enabling debugging helpers that make
development smoother.
"""

from .base import *  # noqa: F401,F403

DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
CORS_ALLOW_ALL_ORIGINS = True if not CORS_ALLOWED_ORIGINS else False
