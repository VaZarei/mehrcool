"""Core template tags: responsive pictures, icons, phone links and text rendering.

Registered as a template *builtin* in settings so templates never need ``{% load %}``.
"""

from __future__ import annotations

import json
from typing import Any

from django import template
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString, mark_safe

from apps.core import images
from apps.core.icons import render_icon
from apps.core.models.settings import normalise_phone_for_href
from apps.pages.services import render_text

register = template.Library()


@register.simple_tag
def icon(name: str, css_class: str = "", size: int = 24) -> SafeString:
    """Render a named inline SVG icon.

    Args:
        name: Icon name from :mod:`apps.core.icons`.
        css_class: Extra classes.
        size: Pixel size.

    Returns:
        Safe SVG markup.
    """
    return render_icon(name, css_class, size)


@register.filter
def tel_href(phone: str) -> str:
    """Turn a display phone number into a ``tel:`` URL.

    Args:
        phone: Display phone number.

    Returns:
        ``tel:+44...`` string.
    """
    return f"tel:{normalise_phone_for_href(phone)}"


@register.filter(name="richtext")
def richtext(value: str) -> SafeString:
    """Render admin-typed text (paragraphs, bullets, bold, links) as HTML.

    Args:
        value: Raw text.

    Returns:
        Safe HTML.
    """
    return mark_safe(render_text(value or ""))  # noqa: S308 - admin-authored, escaped internally


@register.filter
def initials(value: str) -> str:
    """First letters of up to two words, for review avatars.

    Args:
        value: A person's name.

    Returns:
        One or two uppercase letters.
    """
    parts = [p for p in (value or "").split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


@register.filter
def stars(rating: int) -> range:
    """Range helper for rendering star icons.

    Args:
        rating: 1–5.

    Returns:
        ``range(rating)`` clamped to 0–5.
    """
    return range(max(0, min(int(rating or 0), 5)))


@register.filter
def split_csv(value: str) -> list[str]:
    """Split a comma-separated string into a stripped list.

    Args:
        value: ``'a, b, c'``.

    Returns:
        ``['a', 'b', 'c']``.
    """
    return [v.strip() for v in (value or "").split(",") if v.strip()]


@register.simple_tag
def picture(
    field: FieldFile | None,
    alt: str = "",
    sizes: str = "100vw",
    widths: str = "480,768,1080,1440",
    css_class: str = "",
    loading: str = "lazy",
    fetchpriority: str = "",
    decoding: str = "async",
) -> SafeString:
    """Render a ``<picture>`` with AVIF/WebP sources, ``srcset``, ``sizes`` and dimensions.

    SVGs render as a plain ``<img>``. Missing files render nothing so templates never break.

    Args:
        field: Image field to render.
        alt: Alt text (pass ``''`` for decorative images).
        sizes: ``sizes`` attribute.
        widths: Comma-separated candidate widths.
        css_class: Class on the ``<img>``.
        loading: ``lazy`` or ``eager``.
        fetchpriority: ``high`` for the LCP image.
        decoding: ``async`` or ``sync``.

    Returns:
        Safe HTML.
    """
    if not field:
        return mark_safe("")
    attrs: dict[str, Any] = {"alt": alt, "loading": loading, "decoding": decoding}
    if css_class:
        attrs["class"] = css_class
    if fetchpriority:
        attrs["fetchpriority"] = fetchpriority

    if images.is_vector(field):
        attrs["src"] = field.url
        return format_html("<img{}>", _attrs(attrs))

    width_list = [int(w) for w in widths.split(",") if w.strip().isdigit()]
    dims = images.source_dimensions(field)
    if dims:
        target = max(width_list) if width_list else dims[0]
        target = min(target, dims[0])
        attrs["width"] = target
        attrs["height"] = round(dims[1] * target / dims[0])
    sources = []
    for fmt in ("avif", "webp"):
        candidates = images.srcset(field, width_list, fmt)
        if candidates:
            sources.append(
                format_html(
                    '<source type="{}" srcset="{}" sizes="{}">',
                    f"image/{fmt}",
                    candidates,
                    sizes,
                )
            )
    fallback = images.get_rendition(field, max(width_list) if width_list else 1440, "jpeg")
    attrs["src"] = fallback.url if fallback else field.url
    img = format_html("<img{}>", _attrs(attrs))
    return format_html("<picture>{}{}</picture>", mark_safe("".join(sources)), img)  # noqa: S308


def _attrs(attrs: dict[str, Any]) -> SafeString:
    """Serialise an attribute dict, escaping values.

    Args:
        attrs: Attribute name/value pairs.

    Returns:
        Leading-space attribute string.
    """
    return format_html_join("", ' {}="{}"', ((k, v) for k, v in attrs.items() if v is not None))


@register.simple_tag
def json_ld(data: dict[str, Any] | list[Any] | None) -> SafeString:
    """Emit a ``<script type="application/ld+json">`` block.

    Args:
        data: Schema dict (or list of dicts). ``None`` renders nothing.

    Returns:
        Safe script tag, with ``</`` escaped so content cannot break out.
    """
    if not data:
        return mark_safe("")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')  # noqa: S308


@register.simple_tag(takes_context=True)
def active_class(context: dict[str, Any], url: str, css_class: str = "is-active") -> str:
    """Return ``css_class`` when the current path starts with ``url``.

    Args:
        context: Template context (needs ``current_path``).
        url: Link URL.
        css_class: Class to return when active.

    Returns:
        The class or ``''``.
    """
    path = context.get("current_path", "")
    if not url or url == "/":
        return css_class if path == "/" and url == "/" else ""
    return css_class if path.startswith(url) else ""


@register.inclusion_tag("partials/cta_phone.html", takes_context=True)
def call_button(
    context: dict[str, Any],
    label: str = "",
    variant: str = "primary",
    size: str = "",
    event: str = "phone_click",
) -> dict[str, Any]:
    """Render the orange emergency call button (the only place orange is used).

    Args:
        context: Template context (needs ``site``).
        label: Button text; defaults to the emergency number.
        variant: ``primary`` (orange) or ``inverse``.
        size: ``lg`` or ``''``.
        event: Analytics event name fired on tap.

    Returns:
        Context for the partial.
    """
    site = context["site"]
    return {
        "site": site,
        "label": label or site.emergency_phone,
        "variant": variant,
        "size": size,
        "event": event,
    }
