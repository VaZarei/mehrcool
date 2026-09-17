"""App configuration for ``apps.leads``."""

from django.apps import AppConfig


class LeadsConfig(AppConfig):
    """Registers the leads app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.leads"
    verbose_name = "Enquiries & leads"
