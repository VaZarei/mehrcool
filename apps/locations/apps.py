"""App configuration for ``apps.locations``."""

from django.apps import AppConfig


class LocationsConfig(AppConfig):
    """Registers the locations app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.locations"
    verbose_name = "Areas we cover"
