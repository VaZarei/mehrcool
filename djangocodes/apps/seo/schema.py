"""schema.org JSON-LD builders.

Every function reads from the database (``SiteSettings``, services, testimonials) and
returns a plain ``dict``. Templates serialise the dict via the ``{% json_ld %}`` tag,
so no structured data is ever hard-coded in HTML.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.conf import settings

if TYPE_CHECKING:
    from apps.core.models import SiteSettings
    from apps.services.models import Service, ServiceCategory

SCHEMA_CONTEXT = "https://schema.org"
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
KNOWS_ABOUT_BASE = [
    "SIC 43220 - Plumbing, heat and air-conditioning installation",
    "F-Gas Regulation (EC 517/2014)",
    "Commercial Cold Room Installation",
    "VRF and VRV Air Conditioning Systems",
    "Cellar Cooling Repairs",
    "Display Refrigeration Maintenance",
]


def absolute_url(path: str) -> str:
    """Prefix a site-relative path with the canonical origin.

    Args:
        path: Path such as ``'/contact/'`` or an already-absolute URL.

    Returns:
        Absolute URL string.
    """
    if path.startswith(("http://", "https://")):
        return path
    return f"{settings.SITE_URL}{path}"


def _media_url(field: Any) -> str:
    """Absolute URL for a file field, or ``''`` if empty.

    Args:
        field: A ``FieldFile`` or falsy value.

    Returns:
        Absolute URL or empty string.
    """
    return absolute_url(field.url) if field else ""


def _phone_schema(phone: str) -> str:
    """Format a phone number in the hyphenated style Google prefers.

    Args:
        phone: Display phone such as ``'+44 77 7888 9080'``.

    Returns:
        ``'+44-77-7888-9080'``.
    """
    return phone.strip().replace(" ", "-")


def organization_id() -> str:
    """Stable ``@id`` for the organisation node.

    Returns:
        URL fragment identifying the business across all pages.
    """
    return f"{settings.SITE_URL}/#organization"


def postal_address(site: SiteSettings) -> dict[str, str]:
    """Build a ``PostalAddress`` node.

    Args:
        site: The site settings singleton.

    Returns:
        schema.org PostalAddress dict.
    """
    street = ", ".join(p for p in (site.address_line_1, site.address_line_2) if p)
    return {
        "@type": "PostalAddress",
        "streetAddress": street,
        "addressLocality": site.city,
        "addressRegion": site.region,
        "postalCode": site.postcode,
        "addressCountry": site.country_code,
    }


def opening_hours(site: SiteSettings) -> list[dict[str, Any]]:
    """Opening hours specification backing up the 24/7 claim.

    Args:
        site: The site settings singleton.

    Returns:
        A list with one ``OpeningHoursSpecification`` covering every day.
    """
    if not site.is_open_24_7:
        return []
    return [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": DAYS_OF_WEEK,
            "opens": "00:00",
            "closes": "23:59",
        }
    ]


def area_served(site: SiteSettings) -> list[dict[str, str]]:
    """Areas served, typed as City for London and AdministrativeArea otherwise.

    Args:
        site: The site settings singleton.

    Returns:
        List of place nodes.
    """
    areas = []
    for name in site.areas_served_list:
        node_type = "City" if name.lower() == "london" else "AdministrativeArea"
        areas.append({"@type": node_type, "name": name})
    return areas


def aggregate_rating(rating: Decimal | float | None, count: int) -> dict[str, str] | None:
    """Build an ``AggregateRating`` if there are reviews to back it.

    Args:
        rating: Average rating (1–5) or ``None``.
        count: Number of reviews.

    Returns:
        AggregateRating dict, or ``None`` when there is nothing to show.
    """
    if not rating or count <= 0:
        return None
    return {
        "@type": "AggregateRating",
        "ratingValue": f"{Decimal(rating):.1f}",
        "reviewCount": str(count),
        "bestRating": "5",
        "worstRating": "1",
    }


def offer_catalog(categories: Iterable[ServiceCategory]) -> dict[str, Any]:
    """Nested ``OfferCatalog`` built from published categories and their services.

    Args:
        categories: Categories with ``services`` prefetched (published only).

    Returns:
        OfferCatalog dict.
    """
    items = []
    for category in categories:
        services = [
            {
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": service.name,
                    "description": service.short_summary,
                    "url": absolute_url(service.get_absolute_url()),
                },
            }
            for service in category.published_services
        ]
        if services:
            items.append(
                {"@type": "OfferCatalog", "name": category.name, "itemListElement": services}
            )
    return {
        "@type": "OfferCatalog",
        "name": "Refrigeration and HVAC Services",
        "itemListElement": items,
    }


def local_business(
    site: SiteSettings,
    categories: Iterable[ServiceCategory],
    rating: Decimal | float | None,
    review_count: int,
    extra_knows_about: Sequence[str] = (),
) -> dict[str, Any]:
    """Homepage ``HVACBusiness`` + ``LocalBusiness`` node.

    Args:
        site: Site settings singleton.
        categories: Published categories with published services prefetched.
        rating: Aggregate rating value.
        review_count: Number of reviews.
        extra_knows_about: Additional expertise strings (e.g. service names).

    Returns:
        Fully populated JSON-LD dict.
    """
    data: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": ["HVACBusiness", "LocalBusiness"],
        "@id": organization_id(),
        "name": site.trading_name,
        "legalName": site.legal_name,
        "url": settings.SITE_URL,
        "description": site.default_meta_description,
        "telephone": _phone_schema(site.emergency_phone),
        "email": site.email,
        "priceRange": site.price_range.replace("£", "$"),
        "address": postal_address(site),
        "areaServed": area_served(site),
        "knowsAbout": list(dict.fromkeys([*KNOWS_ABOUT_BASE, *extra_knows_about])),
        "hasOfferCatalog": offer_catalog(categories),
    }
    if site.company_number:
        data["identifier"] = site.company_number
    if site.founded_date:
        data["foundingDate"] = site.founded_date.isoformat()
    if site.logo_light:
        data["logo"] = _media_url(site.logo_light)
        data["image"] = _media_url(site.hero_poster or site.logo_light)
    if site.hero_video_mp4:
        data["video"] = {
            "@type": "VideoObject",
            "name": f"{site.trading_name} — engineers at work",
            "contentUrl": _media_url(site.hero_video_mp4),
            "thumbnailUrl": _media_url(site.hero_poster) if site.hero_poster else None,
            "description": site.hero_subheadline,
            "uploadDate": site.updated_at.date().isoformat() if site.updated_at else None,
        }
        data["video"] = {k: v for k, v in data["video"].items() if v}
    if site.latitude is not None and site.longitude is not None:
        data["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": float(site.latitude),
            "longitude": float(site.longitude),
        }
    hours = opening_hours(site)
    if hours:
        data["openingHoursSpecification"] = hours
    same_as = [
        u
        for u in (
            site.facebook_url,
            site.instagram_url,
            site.linkedin_url,
            site.x_url,
            site.google_business_url,
            site.checkatrade_url,
        )
        if u
    ]
    if same_as:
        data["sameAs"] = same_as
    agg = aggregate_rating(rating, review_count)
    if agg:
        data["aggregateRating"] = agg
    return data


def breadcrumbs(items: Sequence[tuple[str, str]]) -> dict[str, Any]:
    """``BreadcrumbList`` from ``(name, path)`` pairs.

    Args:
        items: Ordered crumbs; the last one is the current page.

    Returns:
        BreadcrumbList dict.
    """
    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": name,
                "item": absolute_url(path),
            }
            for index, (name, path) in enumerate(items, start=1)
        ],
    }


def service(site: SiteSettings, obj: Service) -> dict[str, Any]:
    """``Service`` node for an individual service page.

    Args:
        site: Site settings singleton.
        obj: The service.

    Returns:
        Service dict linked back to the organisation.
    """
    data: dict[str, Any] = {
        "@context": SCHEMA_CONTEXT,
        "@type": "Service",
        "name": obj.name,
        "serviceType": obj.name,
        "description": obj.short_summary,
        "url": absolute_url(obj.get_absolute_url()),
        "provider": {"@id": organization_id()},
        "areaServed": area_served(site),
    }
    if obj.hero_image:
        data["image"] = _media_url(obj.hero_image)
    brands = [b.name for b in getattr(obj, "brand_list", [])]
    if brands:
        data["brand"] = [{"@type": "Brand", "name": b} for b in brands]
    return data


def faq_page(faqs: Iterable[Any]) -> dict[str, Any] | None:
    """``FAQPage`` node from objects with ``question`` and ``answer`` attributes.

    Args:
        faqs: Iterable of FAQ-like objects.

    Returns:
        FAQPage dict, or ``None`` when there are no FAQs.
    """
    entities = [
        {
            "@type": "Question",
            "name": faq.question,
            "acceptedAnswer": {"@type": "Answer", "text": faq.answer},
        }
        for faq in faqs
    ]
    if not entities:
        return None
    return {"@context": SCHEMA_CONTEXT, "@type": "FAQPage", "mainEntity": entities}


def website(site: SiteSettings) -> dict[str, Any]:
    """``WebSite`` node so the brand name appears correctly in results.

    Args:
        site: Site settings singleton.

    Returns:
        WebSite dict.
    """
    return {
        "@context": SCHEMA_CONTEXT,
        "@type": "WebSite",
        "@id": f"{settings.SITE_URL}/#website",
        "url": settings.SITE_URL,
        "name": site.trading_name,
        "publisher": {"@id": organization_id()},
        "inLanguage": "en-GB",
    }


def reviews(testimonials: Iterable[Any]) -> list[dict[str, Any]]:
    """``Review`` nodes for individual testimonials.

    Args:
        testimonials: Objects with ``author_name``, ``quote``, ``rating``, ``date``.

    Returns:
        List of Review dicts.
    """
    return [
        {
            "@type": "Review",
            "author": {"@type": "Person", "name": t.author_name},
            "reviewBody": t.quote,
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(t.rating),
                "bestRating": "5",
                "worstRating": "1",
            },
            "datePublished": t.date.isoformat() if t.date else None,
            "itemReviewed": {"@id": organization_id()},
        }
        for t in testimonials
    ]
