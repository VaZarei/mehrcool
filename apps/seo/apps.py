"""App configuration for ``apps.seo``."""

from django.apps import AppConfig


class SeoConfig(AppConfig):
    """Registers the SEO app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.seo"
    verbose_name = "Search engine settings"
