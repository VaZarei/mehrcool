"""Create the admin permission groups: Content Editor and Sales."""

from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

CONTENT_APPS = ("core", "pages", "services", "projects", "locations", "testimonials", "redirects")
SALES_APPS = ("leads",)


class Command(BaseCommand):
    """Idempotently create groups and assign model permissions."""

    help = "Create 'Content Editor' and 'Sales' groups with the right permissions"

    def handle(self, *args: object, **options: object) -> None:
        """Create or update the groups."""
        editors, _ = Group.objects.get_or_create(name="Content Editor")
        editors.permissions.set(Permission.objects.filter(content_type__app_label__in=CONTENT_APPS))
        sales, _ = Group.objects.get_or_create(name="Sales")
        sales.permissions.set(Permission.objects.filter(content_type__app_label__in=SALES_APPS))
        self.stdout.write(
            self.style.SUCCESS(
                f"Groups ready: Content Editor ({editors.permissions.count()} permissions), "
                f"Sales ({sales.permissions.count()} permissions)."
            )
        )
