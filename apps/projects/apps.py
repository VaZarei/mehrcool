"""App configuration for ``apps.projects``."""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Registers the projects app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    verbose_name = "Case studies & sectors"
