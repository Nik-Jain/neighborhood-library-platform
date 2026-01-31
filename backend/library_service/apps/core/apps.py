"""
Apps configuration for the core library service.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library_service.apps.core'
    verbose_name = 'Library Core'
