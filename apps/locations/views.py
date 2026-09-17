"""Views for the areas index and borough landing pages."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.views.generic import DetailView, ListView

from apps.core.views import trust_strip_context
from apps.pages.services import page_copy
from apps.projects.models import CaseStudy
from apps.seo import schema
from apps.services.models import Service
from apps.testimonials.models import Testimonial

from .models import AreaRegion, ServiceArea


class AreaListView(ListView):
    """``/areas/``: every area grouped by region."""

    template_name = "locations/area_list.html"
    context_object_name = "areas"

    def get_queryset(self) -> QuerySet[ServiceArea]:
        """Published areas."""
        return ServiceArea.objects.published()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Group areas by region for the template."""
        context = super().get_context_data(**kwargs)
        grouped: dict[str, list[ServiceArea]] = {}
        for area in context["areas"]:
            grouped.setdefault(area.get_region_display(), []).append(area)
        crumbs = [("Home", "/"), ("Areas we cover", "/areas/")]
        copy = page_copy(
            "areas",
            "Areas we cover",
            "Engineers based in Canary Wharf with vans across London, Greater London and "
            "Berkshire. Pick your area for local response times and recent work nearby.",
        )
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "grouped_areas": grouped,
                "region_order": [label for _, label in AreaRegion.choices],
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
            }
        )
        return context


class AreaDetailView(DetailView):
    """Borough landing page pulling local case studies and reviews, with fallbacks."""

    template_name = "locations/area_detail.html"
    context_object_name = "area"

    def get_queryset(self) -> QuerySet[ServiceArea]:
        """Published areas."""
        return ServiceArea.objects.published()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add local proof (or sensible site-wide fallbacks) and schema."""
        context = super().get_context_data(**kwargs)
        area: ServiceArea = context["area"]
        local_cases = list(CaseStudy.objects.published().for_cards().filter(area=area)[:3])
        local_reviews = list(Testimonial.objects.published().filter(area=area)[:3])
        crumbs = [
            ("Home", "/"),
            ("Areas we cover", "/areas/"),
            (area.name, area.get_absolute_url()),
        ]
        context.update(
            {
                "seo": area,
                "case_studies": local_cases
                or list(CaseStudy.objects.published().for_cards().filter(is_featured=True)[:3]),
                "case_studies_are_local": bool(local_cases),
                "reviews": local_reviews or list(Testimonial.objects.featured()[:3]),
                "reviews_are_local": bool(local_reviews),
                "services": Service.objects.published().for_cards().filter(is_featured=True)[:6],
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                **trust_strip_context(),
            }
        )
        return context
