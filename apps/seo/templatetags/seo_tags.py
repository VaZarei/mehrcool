"""``{% meta_tags %}``: title, description, canonical, robots, Open Graph and Twitter cards."""

from __future__ import annotations

from typing import Any

from django import template
from django.conf import settings

from apps.seo.models import META_TITLE_MAX

register = template.Library()


@register.inclusion_tag("seo/meta_tags.html", takes_context=True)
def meta_tags(context: dict[str, Any]) -> dict[str, Any]:
    """Compute every head meta tag from the ``seo`` object or page-level overrides.

    Resolution order for each value: explicit ``page_title``/``page_description`` context
    variables → ``seo`` object's SEO fields → the object's own title/summary → site
    defaults from ``SiteSettings``.

    Args:
        context: Template context.

    Returns:
        Context for ``seo/meta_tags.html``.
    """
    site = context["site"]
    request = context.get("request")
    seo = context.get("seo")

    title = context.get("page_title") or (seo.get_seo_title() if seo else "")
    if title and not (seo and seo.meta_title):
        title = f"{title}{site.default_meta_title_suffix}"
    if not title:
        title = site.trading_name
    description = (
        context.get("page_description")
        or (seo.get_seo_description() if seo else "")
        or site.default_meta_description
    )
    path = request.path if request else "/"
    canonical = (
        seo.canonical_url if seo and seo.canonical_url else ""
    ) or f"{settings.SITE_URL}{path}"
    og_field = (seo.get_og_image_field() if seo else None) or site.default_og_image or None
    og_image = f"{settings.SITE_URL}{og_field.url}" if og_field else ""
    noindex = bool(context.get("noindex")) or bool(seo and seo.noindex)
    return {
        "title": title[: META_TITLE_MAX + len(site.default_meta_title_suffix)],
        "description": description,
        "canonical": canonical,
        "og_image": og_image,
        "og_type": context.get("og_type", "website"),
        "noindex": noindex,
        "site": site,
    }
