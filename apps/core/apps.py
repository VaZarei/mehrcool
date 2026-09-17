"""App configuration for ``apps.core``."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Registers the core app and wires up signal handlers on ready."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Site settings & navigation"

    def ready(self) -> None:
        """Import signal handlers so cache invalidation is connected."""
        from . import signals  # noqa: F401
