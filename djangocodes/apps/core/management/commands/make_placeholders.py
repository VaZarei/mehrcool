"""Generate placeholder media into ``media/placeholders/`` (also used by ``seed_demo``)."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.core import placeholders as ph


class Command(BaseCommand):
    """Create branded SVG/JPEG/video stand-ins listed in ASSETS_NEEDED.md."""

    help = "Generate branded placeholder logos, images and hero video"

    def handle(self, *args: object, **options: object) -> None:
        """Write every placeholder asset."""
        ph.write_svg("logo-light.svg", ph.logo_svg(False))
        ph.write_svg("logo-dark.svg", ph.logo_svg(True))
        ph.write_svg("favicon.svg", ph.favicon_svg())
        ph.scene_jpeg("hero-poster.jpg", 1920, 1080, seed=1)
        mp4, webm = ph.hero_video()
        self.stdout.write(self.style.SUCCESS(f"Placeholders written to {ph.PLACEHOLDER_DIR}"))
        if not mp4:
            self.stdout.write(self.style.WARNING("Hero video skipped (ffmpeg unavailable)."))
