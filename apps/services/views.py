"""Views for service category hubs and individual service pages."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from apps.core.models import SiteSettings
from apps.core.views import trust_strip_context
from apps.pages.models import BlockType
from apps.pages.services import page_copy
from apps.projects.models import CaseStudy
from apps.seo import schema
from apps.testimonials.models import Testimonial

from .models import Service, ServiceCategory


class ServiceIndexView(ListView):
    """``/services/``: every category with its services, for buyers who browse."""

    template_name = "services/index.html"
    context_object_name = "categories"

    def get_queryset(self) -> Any:
        """Published categories with published services prefetched."""
        return ServiceCategory.objects.published().with_published_services()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add breadcrumbs and schema."""
        context = super().get_context_data(**kwargs)
        crumbs = [("Home", "/"), ("Services", "/services/")]
        copy = page_copy(
            "services",
            "Commercial refrigeration & air conditioning services",
            "Every service we offer, grouped the way facilities teams buy them.",
        )
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                "audience": "Contract buyers (Path B)",
                **trust_strip_context(),
            }
        )
        return context


def render_category(request: HttpRequest, category: ServiceCategory) -> HttpResponse:
    """Render a category hub (called by the slug dispatcher).

    Args:
        request: Current request.
        category: Published category with ``published_services`` prefetched.

    Returns:
        Rendered response.
    """
    crumbs = [("Home", "/"), (category.name, category.get_absolute_url())]
    case_studies = (
        CaseStudy.objects.published().for_cards().filter(services__category=category).distinct()[:3]
    )
    context = {
        "category": category,
        "seo": category,
        "services": category.published_services,
        "case_studies": case_studies,
        "breadcrumbs": crumbs,
        "schema_graph": [schema.breadcrumbs(crumbs)],
        "audience": category.audience,
        **trust_strip_context(),
    }
    return render(request, "services/category.html", context)


def category_view(request: HttpRequest, category_slug: str) -> HttpResponse:
    """``/<slug>/`` entry point: try a category hub, then fall back to a content page.

    Registered under the ``services`` namespace so ``ServiceCategory.get_absolute_url``
    reverses cleanly; the actual lookup order lives in ``apps.core.views.slug_dispatch``.

    Args:
        request: Current request.
        category_slug: URL segment.

    Returns:
        Rendered response.
    """
    from apps.core.views import slug_dispatch

    return slug_dispatch(request, category_slug)


def service_detail(request: HttpRequest, category_slug: str, slug: str) -> HttpResponse:
    """Individual service page with specs, FAQs, blocks, proof and schema.

    Args:
        request: Current request.
        category_slug: Parent category slug.
        slug: Service slug.

    Returns:
        Rendered response.
    """
    service = get_object_or_404(
        Service.objects.published().for_detail(), category__slug=category_slug, slug=slug
    )
    site = SiteSettings.load()
    faqs = list(service.faqs.all())
    blocks = list(service.blocks.all())
    block_faqs = [e for b in blocks if b.block_type == BlockType.FAQ for e in b.faq_entries]
    crumbs = [
        ("Home", "/"),
        (service.category.name, service.category.get_absolute_url()),
        (service.name, service.get_absolute_url()),
    ]
    case_studies = list(service.related_case_studies.published().for_cards()[:3]) or list(
        CaseStudy.objects.published().for_cards().filter(services=service)[:3]
    )
    context = {
        "service": service,
        "seo": service,
        "specs": list(service.specifications.all()),
        "faqs": faqs,
        "blocks": blocks,
        "brands": getattr(service, "brand_list", []),
        "related_services": getattr(service, "related_list", []),
        "case_studies": case_studies,
        "reviews": Testimonial.objects.published().filter(service=service)[:3],
        "breadcrumbs": crumbs,
        "schema_graph": [
            schema.service(site, service),
            schema.breadcrumbs(crumbs),
            schema.faq_page([*faqs, *block_faqs]),
        ],
        "audience": "Emergency callers" if service.is_emergency else "Contract buyers (Path B)",
        **trust_strip_context(),
    }
    return render(request, "services/detail.html", context)
