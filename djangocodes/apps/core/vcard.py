"""vCard and QR generation for the 'save our contact' feature."""

from __future__ import annotations

import io

import segno

from django.conf import settings

from .models import SiteSettings
from .models.settings import normalise_phone_for_href


def build_vcard(site: SiteSettings) -> str:
    """Build a vCard 3.0 string from site settings.

    Args:
        site: Site settings singleton.

    Returns:
        vCard text with CRLF line endings.
    """
    street = ";".join(p for p in (site.address_line_1, site.address_line_2) if p)
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:;{site.trading_name};;;",
        f"FN:{site.trading_name}",
        f"ORG:{site.legal_name}",
        f"TEL;TYPE=CELL,VOICE:{normalise_phone_for_href(site.emergency_phone)}",
        f"EMAIL;TYPE=WORK:{site.email}",
        f"ADR;TYPE=WORK:;;{street};{site.city};{site.region};{site.postcode};{site.country_code}",
        f"URL:{settings.SITE_URL}",
        f"NOTE:{site.opening_hours_text}",
        "END:VCARD",
    ]
    if site.whatsapp_number and site.whatsapp_number != site.emergency_phone:
        lines.insert(6, f"TEL;TYPE=WORK,VOICE:{normalise_phone_for_href(site.whatsapp_number)}")
    return "\r\n".join(lines) + "\r\n"


def vcard_qr_svg(site: SiteSettings, dark: str = "#2B3E8C") -> bytes:
    """Render the vCard as an SVG QR code.

    Args:
        site: Site settings singleton.
        dark: Module colour (hex).

    Returns:
        SVG bytes.
    """
    qr = segno.make(build_vcard(site), error="m")
    buffer = io.BytesIO()
    qr.save(buffer, kind="svg", scale=8, border=2, dark=dark, light=None, xmldecl=False)
    return buffer.getvalue()
