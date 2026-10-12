"""Populate a fully demo-ready site: settings, media placeholders, catalogue, proof, pages."""

from __future__ import annotations

from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.seed.catalogue import seed_form_choices, seed_services
from apps.core.seed.pages import seed_pages
from apps.core.seed.proof import seed_areas, seed_case_studies, seed_sectors, seed_testimonials
from apps.core.seed.site import seed_intent_cards, seed_navigation, seed_site_settings, seed_trust


class Command(BaseCommand):
    """Idempotent seed: safe to re-run; updates existing rows by slug."""

    help = "Seed demo content and placeholder media so the site is fully populated"

    def add_arguments(self, parser) -> None:  # type: ignore[no-untyped-def]
        """Add ``--no-video`` to skip ffmpeg."""
        parser.add_argument("--skip-groups", action="store_true", help="Do not create admin groups")

    @transaction.atomic
    def handle(self, *args: object, **options: object) -> None:
        """Run every seed step in dependency order."""
        steps = [
            ("Site settings & placeholder media", seed_site_settings),
            ("Accreditations, brands, clients", seed_trust),
            ("Form dropdown options", seed_form_choices),
            ("Service categories & services", seed_services),
            ("Sectors", seed_sectors),
            ("Service areas", seed_areas),
            ("Reviews", seed_testimonials),
            ("Case studies", seed_case_studies),
            ("Pages", seed_pages),
            ("'I need…' tiles", seed_intent_cards),
            ("Navigation", seed_navigation),
        ]
        verbose = int(options.get("verbosity", 1)) > 0
        for label, fn in steps:
            fn()
            if verbose:
                self.stdout.write(f"  [ok] {label}")
        cache.clear()
        if not options.get("skip_groups"):
            call_command("setup_groups", verbosity=options.get("verbosity", 1))
        if verbose:
            self.stdout.write(
                self.style.SUCCESS(
                    "Demo site seeded. Create a superuser with: manage.py createsuperuser"
                )
            )
