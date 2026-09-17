"""robots.txt generated from settings so the sitemap URL is always right."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

DISALLOWED_PATHS = [
    "/admin/",
    "/styleguide/",
    "/contact/thank-you/",
    "/emergency-callout/thank-you/",
]


@require_GET
@cache_control(max_age=86400)
def robots_txt(request: HttpRequest) -> HttpResponse:
    """Serve robots.txt.

    Args:
        request: Current request.

    Returns:
        ``text/plain`` response.
    """
    lines = ["User-agent: *", *[f"Disallow: {p}" for p in DISALLOWED_PATHS], ""]
    lines.append(f"Sitemap: {settings.SITE_URL}/sitemap.xml")
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
