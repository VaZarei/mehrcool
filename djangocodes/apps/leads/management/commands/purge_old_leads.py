"""Delete enquiries and repair requests older than the retention period in the privacy policy."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.leads.models import ContactEnquiry, RepairRequest


class Command(BaseCommand):
    """Run daily/weekly from cron: ``python manage.py purge_old_leads``."""

    help = "Delete lead records (and repair photos) older than --days (default 730 = 24 months)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--days", type=int, default=730)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        cutoff = timezone.now() - timedelta(days=options["days"])
        enquiries = ContactEnquiry.objects.filter(created_at__lt=cutoff)
        repairs = RepairRequest.objects.filter(created_at__lt=cutoff)
        self.stdout.write(f"{enquiries.count()} enquiries, {repairs.count()} repair requests older than {cutoff:%Y-%m-%d}")
        if options["dry_run"]:
            return
        for repair in repairs.iterator():
            if repair.equipment_photo:
                repair.equipment_photo.delete(save=False)
        repairs.delete()
        enquiries.delete()
        self.stdout.write(self.style.SUCCESS("Purged."))
