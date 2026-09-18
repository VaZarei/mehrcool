"""Concatenate and lightly minify the layered CSS into single deployable files.

``main.css`` stays the human-readable import index; this command follows its
``@import`` order to produce ``main.min.css`` (deferred) and ``critical.min.css``
(inlined in ``<head>``) so production never pays an ``@import`` waterfall.
"""

from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

CSS_DIR = Path(settings.BASE_DIR) / "static" / "css"
IMPORT_RE = re.compile(r'@import\s+url\(["\']?([^"\')]+)["\']?\);')
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)

# Files whose rules affect above-the-fold layout on every page.
CRITICAL_FILES = [
    "02-reset.css",
    "03-base.css",
    "04-layout.css",
    "05-components/button.css",
    "05-components/banner.css",
    "05-components/header.css",
    "05-components/nav.css",
    "05-components/hero.css",
    "05-components/page-hero.css",
    "05-components/mobile-bar.css",
    "05-components/breadcrumb.css",
    "05-components/emergency.css",
    "06-animations.css",
    "07-utilities.css",
]
# 08-preferences.css is deliberately NOT inlined: it carries an override for
# every component on the site, most of it below the fold. The motion it needs
# to suppress above the fold is handled inside 06-animations.css instead.


def minify(css: str) -> str:
    """Strip comments and collapse whitespace without touching string contents.

    Args:
        css: Raw CSS.

    Returns:
        Compact CSS.
    """
    css = COMMENT_RE.sub("", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()


def import_order(index_file: Path) -> list[str]:
    """Read ``@import`` targets from the index file in order.

    Args:
        index_file: Path to ``main.css``.

    Returns:
        Relative file paths.
    """
    return IMPORT_RE.findall(index_file.read_text(encoding="utf-8"))


class Command(BaseCommand):
    """Build ``main.min.css`` and ``critical.min.css`` from the source layers."""

    help = "Concatenate and minify static/css into main.min.css and critical.min.css"

    def handle(self, *args: object, **options: object) -> None:
        """Run the build.

        Args:
            *args: Unused.
            **options: Unused.
        """
        files = import_order(CSS_DIR / "main.css")
        full = "\n".join((CSS_DIR / f).read_text(encoding="utf-8") for f in files)
        critical = "\n".join(
            (CSS_DIR / f).read_text(encoding="utf-8") for f in CRITICAL_FILES if f in files
        )
        (CSS_DIR / "main.min.css").write_text(minify(full), encoding="utf-8")
        (CSS_DIR / "critical.min.css").write_text(minify(critical), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Built main.min.css ({len(minify(full)) // 1024} KB) and "
                f"critical.min.css ({len(minify(critical)) // 1024} KB) from {len(files)} files."
            )
        )
