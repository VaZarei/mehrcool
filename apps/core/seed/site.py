"""Seed: site settings, navigation, trust badges, brands, clients, intent tiles."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from django.contrib.sites.models import Site

from apps.core import placeholders as ph
from apps.core.models import (
    BrandServiced,
    ClientLogo,
    IntentCard,
    LinkTarget,
    NavigationItem,
    SiteSettings,
    TrustBadge,
)


def attach(field, path: Path | None, name: str | None = None) -> None:  # type: ignore[no-untyped-def]
    """Attach a file on disk to a FileField if the field is empty.

    Args:
        field: The ``FieldFile``.
        path: Source path.
        name: Stored filename (defaults to the source name).
    """
    if path is None or field:
        return
    # Reference the placeholder in place (no copy) so fixtures dumped from a seeded
    # database resolve against the committed ``media/placeholders/`` directory.
    field.name = f"{ph.PLACEHOLDER_DIR.name}/{name or path.name}"


def seed_site_settings() -> SiteSettings:
    """Create the singleton with the business facts and placeholder media.

    Returns:
        The saved settings row.
    """
    Site.objects.update_or_create(
        pk=1, defaults={"domain": "mehrcoolrefrigeration.co.uk", "name": "Mehr Cool"}
    )
    site = SiteSettings.load()
    site.company_number = "15733975"
    site.founded_date = date(2024, 5, 22)
    site.google_maps_embed_url = "https://www.google.com/maps?q=51.4912,-0.0151&z=15&output=embed"
    attach(site.logo_light, ph.write_svg("logo-light.svg", ph.logo_svg(False)))
    attach(site.logo_dark, ph.write_svg("logo-dark.svg", ph.logo_svg(True)))
    attach(site.favicon, ph.write_svg("favicon.svg", ph.favicon_svg()))
    attach(site.hero_poster, ph.scene_jpeg("hero-poster.jpg", 1920, 1080, seed=1))
    attach(
        site.default_og_image, ph.scene_jpeg("og-default.jpg", 1200, 630, seed=7, accent=ph.YELLOW)
    )
    mp4, webm = ph.hero_video()
    attach(site.hero_video_mp4, mp4)
    attach(site.hero_video_webm, webm)
    site.save()
    return site


def seed_trust() -> None:
    """Accreditations (inactive by default), brands and client logos."""
    badges = [
        (
            "F-Gas",
            "F-GAS",
            "CERTIFIED",
            ph.NAVY,
            "Legally required to handle refrigerant gases under EC 517/2014.",
            True,
            True,
        ),
        (
            "REFCOM",
            "REFCOM",
            "ELITE",
            "#1E2C66",
            "Refrigerant handling company certification scheme.",
            False,
            False,
        ),
        (
            "SafeContractor",
            "SAFE",
            "CONTRACTOR",
            "#1F8A5B",
            "Health & safety pre-qualification for contractors.",
            False,
            False,
        ),
        (
            "CHAS",
            "CHAS",
            "ACCREDITED",
            "#3D4350",
            "Contractors Health and Safety Assessment Scheme.",
            False,
            False,
        ),
        (
            "ISO 9001",
            "ISO",
            "9001",
            "#4A72C0",
            "Quality management system certification.",
            False,
            False,
        ),
        (
            "Gas Safe",
            "GAS SAFE",
            "REGISTERED",
            "#C2372B",
            "Required for work on gas appliances.",
            False,
            False,
        ),
    ]
    for order, (name, label, sub, colour, desc, active, header) in enumerate(badges):
        badge, _ = TrustBadge.objects.get_or_create(
            name=name,
            defaults={
                "short_description": desc,
                "is_active": active,
                "show_in_header": header,
                "order": order,
            },
        )
        attach(
            badge.logo,
            ph.write_svg(
                f"badge-{name.lower().replace(' ', '-')}.svg", ph.badge_svg(label, sub, colour)
            ),
        )
        badge.save()

    brands = [
        "Daikin",
        "Mitsubishi Electric",
        "Toshiba",
        "Fujitsu",
        "Panasonic",
        "LG",
        "Foster",
        "Williams",
        "Bitzer",
        "Danfoss",
    ]
    for order, name in enumerate(brands):
        brand, _ = BrandServiced.objects.get_or_create(name=name, defaults={"order": order})
        attach(
            brand.logo,
            ph.write_svg(f"brand-{name.lower().replace(' ', '-')}.svg", ph.wordmark_svg(name)),
        )
        brand.save()

    clients = [
        "Dockside Dining Group",
        "Riverside Hotels",
        "Freshmarket Stores",
        "Meridian Offices",
        "Thameside Pharmacy Group",
    ]
    for order, name in enumerate(clients):
        client, _ = ClientLogo.objects.get_or_create(name=name, defaults={"order": order})
        attach(client.logo, ph.write_svg(f"client-{order}.svg", ph.wordmark_svg(name, "#58606F")))
        client.save()


def seed_intent_cards() -> None:
    """The three 'I need…' tiles."""
    tiles = [
        (
            "Repair",
            "Something has stopped working — get an engineer today.",
            "wrench",
            "/emergency-callout/",
            True,
        ),
        (
            "Maintenance",
            "Planned servicing, F-Gas leak checks and compliance records.",
            "calendar-check",
            "/air-conditioning/planned-preventative-maintenance/",
            False,
        ),
        (
            "New installation",
            "Cold rooms, display cases or air conditioning for a new or refitted site.",
            "plus-square",
            "/quote/",
            False,
        ),
    ]
    for order, (label, desc, icon, url, emergency) in enumerate(tiles):
        IntentCard.objects.get_or_create(
            label=label,
            defaults={
                "description": desc,
                "icon": icon,
                "url": url,
                "is_emergency": emergency,
                "order": order,
            },
        )


def seed_navigation() -> None:
    """Header and footer menus, linking to seeded objects by slug."""
    from apps.pages.models import Page
    from apps.services.models import ServiceCategory

    NavigationItem.objects.all().delete()

    def item(label: str, order: int, **kwargs: object) -> NavigationItem:
        return NavigationItem.objects.create(label=label, order=order, **kwargs)

    cat = {c.slug: c for c in ServiceCategory.objects.all()}
    page = {p.slug: p for p in Page.objects.all()}

    services = item(
        "Services", 0, target_type=LinkTarget.URL, url="/services/", show_in_footer=True
    )
    for i, slug in enumerate(
        ("commercial-refrigeration", "air-conditioning", "emergency-services")
    ):
        if slug in cat:
            item(
                cat[slug].name,
                i,
                parent=services,
                target_type=LinkTarget.SERVICE_CATEGORY,
                service_category=cat[slug],
                show_in_footer=True,
            )
    item("Sectors", 1, target_type=LinkTarget.URL, url="/sectors/")
    item("Case studies", 2, target_type=LinkTarget.URL, url="/case-studies/")
    item("Areas", 3, target_type=LinkTarget.URL, url="/areas/")
    about_kwargs = (
        {"target_type": LinkTarget.PAGE, "page": page["about"]}
        if "about" in page
        else {"target_type": LinkTarget.URL, "url": "/about/"}
    )
    item("About", 4, **about_kwargs)
    item("Contact", 5, target_type=LinkTarget.URL, url="/contact/")

    company = item(
        "Company", 10, target_type=LinkTarget.NONE, show_in_header=False, show_in_footer=True
    )
    for i, (label, slug) in enumerate(
        (
            ("About us", "about"),
            ("Careers", "careers"),
            ("F-Gas compliance statement", "f-gas-compliance"),
        )
    ):
        if slug in page:
            item(
                label,
                i,
                parent=company,
                target_type=LinkTarget.PAGE,
                page=page[slug],
                show_in_header=False,
                show_in_footer=True,
            )
    item(
        "Case studies",
        3,
        parent=company,
        target_type=LinkTarget.URL,
        url="/case-studies/",
        show_in_header=False,
        show_in_footer=True,
    )
    item(
        "Areas we cover",
        4,
        parent=company,
        target_type=LinkTarget.URL,
        url="/areas/",
        show_in_header=False,
        show_in_footer=True,
    )

    legal = item(
        "Legal", 11, target_type=LinkTarget.NONE, show_in_header=False, show_in_footer=True
    )
    for i, (label, slug) in enumerate(
        (
            ("Terms of business", "terms"),
            ("Privacy policy", "privacy"),
            ("Cookie policy", "cookies"),
        )
    ):
        if slug in page:
            item(
                label,
                i,
                parent=legal,
                target_type=LinkTarget.PAGE,
                page=page[slug],
                show_in_header=False,
                show_in_footer=True,
            )
