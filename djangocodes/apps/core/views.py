"""Thin views for the homepage, styleguide, contact card and error pages."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from apps.pages.models import Page
from apps.projects.models import CaseStudy
from apps.seo import schema
from apps.services.models import Service, ServiceCategory
from apps.testimonials.models import Testimonial

from .models import BrandServiced, ClientLogo, IntentCard, SiteSettings, TrustBadge
from .vcard import build_vcard, vcard_qr_svg


def trust_strip_context() -> dict[str, Any]:
    """Logos for the trust strip and CTA bands.

    Returns:
        Dict with ``badges``, ``brands`` and ``clients`` querysets.
    """
    return {
        "badges": TrustBadge.objects.filter(is_active=True),
        "brands": BrandServiced.objects.filter(is_active=True),
        "clients": ClientLogo.objects.filter(is_active=True),
    }


class HomeView(TemplateView):
    """Homepage: hero, intent strip, trust strip, services, proof, reviews, CTA."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Assemble every homepage section in a fixed number of queries.

        Returns:
            Template context.
        """
        context = super().get_context_data(**kwargs)
        site: SiteSettings = SiteSettings.load()
        categories = list(
            ServiceCategory.objects.published().with_published_services().order_by("order")
        )
        featured_services = list(
            Service.objects.published().for_cards().filter(is_featured=True)[:6]
        )
        rating, count = Testimonial.objects.aggregate_rating()
        if site.google_rating_override:
            rating = site.google_rating_override
        if site.google_review_count_override:
            count = site.google_review_count_override
        featured_reviews = list(Testimonial.objects.featured()[:6])
        context.update(
            {
                "categories": categories,
                "featured_services": featured_services,
                "intent_cards": IntentCard.objects.filter(is_active=True),
                "case_studies": CaseStudy.objects.published()
                .for_cards()
                .filter(is_featured=True)[:3],
                "reviews": featured_reviews,
                "rating": rating,
                "review_count": count,
                "schema_graph": [
                    schema.local_business(
                        site,
                        categories,
                        rating,
                        count,
                        extra_knows_about=[s.name for s in featured_services],
                    ),
                    schema.website(site),
                ],
                "audience": "both",
                **trust_strip_context(),
            }
        )
        return context


# The stylesheet holds literal values, not custom properties, so the styleguide
# carries its own copy of the palette and spacing ladder purely to label the
# swatches. Keep it in step with static/css when a value changes.
PALETTE = [
    ("navy-900", "#151f47"),
    ("navy-800", "#1e2c66"),
    ("navy-700", "#2b3e8c"),
    ("navy-600", "#34499e"),
    ("navy-500", "#4a72c0"),
    ("ice-400", "#6f93d4"),
    ("ice-300", "#a7bfe8"),
    ("ice-200", "#d5e1f5"),
    ("ice-100", "#eaf0fa"),
    ("ice-50", "#f4f7fb"),
    ("amber-600", "#d3860c"),
    ("amber-500", "#f29d12"),
    ("amber-400", "#f7b23d"),
    ("yellow-400", "#ffc82b"),
    ("yellow-100", "#fff4d1"),
    ("grey-900", "#111111"),
    ("grey-800", "#262a33"),
    ("grey-700", "#3d4350"),
    ("grey-600", "#58606f"),
    ("grey-500", "#737b8a"),
    ("grey-400", "#9aa1ad"),
    ("grey-300", "#c3c8d1"),
    ("grey-200", "#e1e4ea"),
    ("grey-100", "#f1f3f6"),
    ("success", "#1f8a5b"),
    ("error", "#c2372b"),
]

SPACING_SCALE = [
    ("1", "0.25rem"),
    ("2", "0.5rem"),
    ("3", "0.75rem"),
    ("4", "1rem"),
    ("5", "1.25rem"),
    ("6", "1.5rem"),
    ("8", "2rem"),
    ("10", "2.5rem"),
    ("12", "3rem"),
    ("16", "4rem"),
    ("20", "5rem"),
    ("24", "6rem"),
]


class StyleguideView(TemplateView):
    """Developer-only page rendering every colour, size and component."""

    template_name = "core/styleguide.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Hide the styleguide unless enabled in settings.

        Raises:
            Http404: When ``STYLEGUIDE_ENABLED`` is false.
        """
        if not settings.STYLEGUIDE_ENABLED:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add sample objects for component previews."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "sample_service": Service.objects.published().for_cards().first(),
                "sample_review": Testimonial.objects.published().first(),
                "palette": PALETTE,
                "spacing_scale": SPACING_SCALE,
                "icon_names": [
                    "wrench",
                    "calendar-check",
                    "plus-square",
                    "snowflake",
                    "wind",
                    "bolt",
                    "shield-check",
                    "clock",
                    "phone",
                    "map-pin",
                    "thermometer",
                    "building",
                    "whatsapp",
                ],
                **trust_strip_context(),
            }
        )
        return context


@cache_control(max_age=3600)
def vcard_download(request: HttpRequest) -> HttpResponse:
    """Serve the company contact card as a downloadable ``.vcf`` file.

    Args:
        request: Current request.

    Returns:
        ``text/vcard`` response.
    """
    site = SiteSettings.load()
    response = HttpResponse(build_vcard(site), content_type="text/vcard; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="mehr-cool.vcf"'
    return response


@cache_control(max_age=3600)
def vcard_qr(request: HttpRequest) -> HttpResponse:
    """Serve an auto-generated QR code (SVG) encoding the contact card.

    Used when no designed QR image has been uploaded in Site settings.

    Args:
        request: Current request.

    Returns:
        ``image/svg+xml`` response.
    """
    return HttpResponse(vcard_qr_svg(SiteSettings.load()), content_type="image/svg+xml")


def slug_dispatch(request: HttpRequest, slug: str) -> HttpResponse:
    """Route ``/<slug>/`` to a service category hub or a content page.

    Categories win so the keyword-rich service URLs stay flat; pages fill the rest.

    Args:
        request: Current request.
        slug: URL segment.

    Returns:
        Rendered response.

    Raises:
        Http404: If neither a category nor a page matches.
    """
    from apps.pages.views import render_page
    from apps.services.views import render_category

    category = (
        ServiceCategory.objects.published().with_published_services().filter(slug=slug).first()
    )
    if category is not None:
        return render_category(request, category)
    page = Page.objects.published().prefetch_related("blocks__gallery_images").filter(slug=slug)
    page_obj = page.first()
    if page_obj is not None:
        return render_page(request, page_obj)
    raise Http404


def page_not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    """Branded 404 with the emergency number.

    Args:
        request: Current request.
        exception: The raised ``Http404`` (unused).

    Returns:
        404 response.
    """
    return render(request, "404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    """Branded 500 that tolerates database failure so it always renders.

    Contact details come from ``SiteSettings`` when reachable, otherwise from the
    ``EMERGENCY_PHONE_FALLBACK`` environment setting — never from the template.

    Args:
        request: Current request.

    Returns:
        500 response.
    """
    from django.template import loader

    from .models.settings import normalise_phone_for_href

    phone = settings.EMERGENCY_PHONE_FALLBACK
    trading_name = settings.TRADING_NAME_FALLBACK
    try:
        site = SiteSettings.load()
        phone, trading_name = site.emergency_phone, site.trading_name
    except Exception:  # noqa: BLE001 - the database may be the thing that is broken
        pass
    html = loader.render_to_string(
        "500.html",
        {
            "phone": phone,
            "tel_href": f"tel:{normalise_phone_for_href(phone)}",
            "trading_name": trading_name,
            "debug": settings.DEBUG,
        },
    )
    return HttpResponse(html, status=500)
