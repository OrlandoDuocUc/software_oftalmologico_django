"""
Expose default settings module.

Importing everything from local keeps the developer experience simple
while production deployments can point DJANGO_SETTINGS_MODULE to
config.settings.production.
"""

from .local import *  # noqa: F401,F403
