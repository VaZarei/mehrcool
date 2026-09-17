"""App configuration for ``apps.testimonials``."""

from django.apps import AppConfig


class TestimonialsConfig(AppConfig):
    """Registers the testimonials app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.testimonials"
    verbose_name = "Reviews & testimonials"
