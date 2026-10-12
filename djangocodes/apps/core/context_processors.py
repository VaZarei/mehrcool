"""Template context processors exposing site settings and navigation everywhere."""

from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

from .constants import CACHE_TIMEOUT_SECONDS, NAVIGATION_CACHE_KEY
from .models import NavigationItem, SiteSettings, TrustBadge


def site_settings(request: HttpRequest) -> dict[str, object]:
    """Add the ``site`` singleton and a few globals to every template.

    Args:
        request: Current request.

    Returns:
        Context with ``site``, ``SITE_URL`` and ``header_badge``.
    """
    site = SiteSettings.load()
    badges = _active_badges()
    return {
        "site": site,
        "SITE_URL": settings.SITE_URL,
        "trust_badges": badges,
        "header_badge": next((b for b in badges if b.show_in_header), None),
        "DEBUG": settings.DEBUG,
    }


def _active_badges() -> list[TrustBadge]:
    """Active accreditation badges, cached (used by header, footer and CTA bands).

    Returns:
        Ordered list of badges.
    """
    key = "core:trust_badges:v1"
    badges = cache.get(key)
    if badges is None:
        badges = list(TrustBadge.objects.filter(is_active=True))
        cache.set(key, badges, CACHE_TIMEOUT_SECONDS)
    return badges


def navigation(request: HttpRequest) -> dict[str, object]:
    """Add header and footer navigation trees to every template.

    Both trees are built from one query and cached; children are attached in Python so
    templates never trigger extra queries.

    Args:
        request: Current request.

    Returns:
        Context with ``header_nav`` and ``footer_nav`` lists of top-level items.
    """
    trees = cache.get(NAVIGATION_CACHE_KEY)
    if trees is None:
        items = list(
            NavigationItem.objects.filter(is_active=True)
            .select_related("service_category", "service", "page", "location")
            .order_by("order", "pk")
        )
        by_parent: dict[int | None, list[NavigationItem]] = {}
        for item in items:
            by_parent.setdefault(item.parent_id, []).append(item)
        for item in items:
            item.child_items = by_parent.get(item.pk, [])
            item.resolved_url = item.get_url()
            for child in item.child_items:
                child.resolved_url = child.get_url()
                child.child_items = []
        roots = by_parent.get(None, [])
        trees = {
            "header_nav": [i for i in roots if i.show_in_header],
            "footer_nav": [i for i in roots if i.show_in_footer],
        }
        cache.set(NAVIGATION_CACHE_KEY, trees, CACHE_TIMEOUT_SECONDS)
    return {**trees, "current_path": request.path}
