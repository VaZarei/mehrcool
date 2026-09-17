"""Responsive QA: screenshot key pages at the brief's breakpoints and flag horizontal overflow.

Usage (dev server must be running):
    python scripts/responsive_check.py http://127.0.0.1:8000 out_dir

Requires: pip install playwright && python -m playwright install chromium
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTHS = [320, 375, 414, 768, 1024, 1440, 1920]
PAGES = [
    "/",
    "/emergency-callout/",
    "/commercial-refrigeration/",
    "/commercial-refrigeration/walk-in-cold-rooms/",
    "/contact/",
    "/case-studies/",
    "/case-studies/walk-in-freezer-replacement-soho-restaurant-group/",
    "/areas/air-conditioning-refrigeration-canary-wharf/",
    "/sectors/restaurants/",
    "/about/",
    "/privacy/",
]
SCREENSHOT_WIDTHS = {375, 1440}


def main(base: str, out_dir: str) -> int:
    """Run the checks.

    Args:
        base: Origin of the running dev server.
        out_dir: Directory for screenshots.

    Returns:
        Process exit code (1 if any overflow was found).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            context = browser.new_context(
                viewport={"width": width, "height": 900},
                device_scale_factor=1,
                is_mobile=width < 768,
                has_touch=width < 768,
            )
            page = context.new_page()
            for path in PAGES:
                page.goto(base + path, wait_until="networkidle")
                metrics = page.evaluate(
                    "() => ({sw: document.documentElement.scrollWidth, "
                    "cw: document.documentElement.clientWidth, "
                    "sources: document.querySelectorAll('video source').length, "
                    "h1: document.querySelectorAll('h1').length})"
                )
                if metrics["sw"] > metrics["cw"]:
                    problems.append(
                        f"{width}px {path}: scrollWidth {metrics['sw']} > {metrics['cw']}"
                    )
                if path == "/":
                    expect_video = width >= 768
                    if bool(metrics["sources"]) != expect_video:
                        problems.append(
                            f"{width}px hero video sources={metrics['sources']} (expected "
                            f"{'attached' if expect_video else 'none'})"
                        )
                if width in SCREENSHOT_WIDTHS:
                    name = path.strip("/").replace("/", "_") or "home"
                    page.screenshot(path=str(out / f"{name}-{width}.png"), full_page=True)
                print(f"ok {width:>4}px {path}  (video sources: {metrics['sources']})")
            context.close()

        # Reduced motion: no video sources even on desktop.
        context = browser.new_context(
            viewport={"width": 1440, "height": 900}, reduced_motion="reduce"
        )
        page = context.new_page()
        page.goto(base + "/", wait_until="networkidle")
        if page.evaluate("document.querySelectorAll('video source').length"):
            problems.append("prefers-reduced-motion: video sources were attached")
        context.close()
        browser.close()

    print(
        "\n".join(problems) if problems else "\nNo horizontal overflow; hero video gating correct."
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(
        main(
            sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000",
            sys.argv[2] if len(sys.argv) > 2 else "screenshots",
        )
    )
