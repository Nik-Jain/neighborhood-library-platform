"""
Apps configuration for the core library service.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library_service.apps.core'
    verbose_name = 'Library Core'

    def ready(self):
        """Connect signal handlers."""
        # Import signals to ensure they are registered when app is ready.
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid raising during app loading; signals are best-effort
            pass
