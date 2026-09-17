"""Inline SVG icon set (24 × 24, stroke-based) selectable by name in the admin.

Icons are plain path data so they inherit ``currentColor`` and scale with text.
"""

from __future__ import annotations

from django.utils.html import format_html
from django.utils.safestring import SafeString

ICON_PATHS: dict[str, str] = {
    "wrench": (
        "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 "
        "6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
    ),
    "calendar-check": (
        "M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 "
        "0 1 2-2zM9 16l2 2 4-4"
    ),
    "plus-square": "M3 5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM12 8v8M8 12h8",
    "snowflake": (
        "M12 2v20M4.93 4.93l14.14 14.14M2 12h20M4.93 19.07 19.07 4.93M12 2l-2 3M12 2l2 3M12 22l-2-3"
        "M12 22l2-3M2 12l3-2M2 12l3 2M22 12l-3-2M22 12l-3 2"
    ),
    "wind": "M9.6 4.6A2 2 0 1 1 11 8H2M12.6 19.4A2 2 0 1 0 14 16H2M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2",
    "bolt": "M13 2 3 14h9l-1 8 10-12h-9l1-8z",
    "shield-check": "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM9 12l2 2 4-4",
    "clock": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 6v6l4 2",
    "phone": (
        "M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 "
        "19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 "
        "0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 "
        "2.81.7A2 2 0 0 1 22 16.92z"
    ),
    "map-pin": "M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0zM12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
    "thermometer": "M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z",
    "building": ("M3 21h18M5 21V7l7-4 7 4v14M9 9h1M9 13h1M9 17h1M14 9h1M14 13h1M14 17h1"),
    "whatsapp": (
        "M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21zM9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 "
        "0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"
    ),
    "arrow-right": "M5 12h14M12 5l7 7-7 7",
    "chevron-down": "M6 9l6 6 6-6",
    "check": "M20 6 9 17l-5-5",
    "star": "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z",
    "menu": "M4 6h16M4 12h16M4 18h16",
    "close": "M18 6 6 18M6 6l12 12",
    "mail": "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zM22 6l-10 7L2 6",
    "external": "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3",
    "qr": "M3 3h6v6H3zM15 3h6v6h-6zM3 15h6v6H3zM15 15h2v2h-2zM19 15h2v2h-2zM15 19h2v2h-2zM19 19h2v2h-2z",
}


def render_icon(name: str, css_class: str = "", size: int = 24) -> SafeString:
    """Render a named icon as inline SVG.

    Args:
        name: Key in :data:`ICON_PATHS`. Unknown names render a neutral circle.
        css_class: Extra CSS classes for the ``<svg>``.
        size: Width/height attribute in pixels.

    Returns:
        Safe SVG markup with ``aria-hidden`` set (decorative).
    """
    path = ICON_PATHS.get(name, "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z")
    classes = f"icon icon--{name}" + (f" {css_class}" if css_class else "")
    return format_html(
        '<svg class="{}" width="{}" height="{}" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="{}"/></svg>',
        classes,
        size,
        size,
        path,
    )
