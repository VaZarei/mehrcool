"""App configuration for ``apps.services``."""

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    """Registers the services app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services"
    verbose_name = "Services"
