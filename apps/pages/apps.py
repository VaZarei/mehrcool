"""App configuration for ``apps.pages``."""

from django.apps import AppConfig


class PagesConfig(AppConfig):
    """Registers the pages app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    verbose_name = "Pages & content blocks"
