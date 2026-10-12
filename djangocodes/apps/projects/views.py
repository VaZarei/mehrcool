"""Views for sectors and case studies (listings and detail)."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.views.generic import DetailView, ListView

from apps.core.views import trust_strip_context
from apps.locations.models import ServiceArea
from apps.pages.services import page_copy
from apps.seo import schema
from apps.services.models import Service

from .models import CaseStudy, Sector


class SectorListView(ListView):
    """``/sectors/``: index of markets served."""

    template_name = "projects/sector_list.html"
    context_object_name = "sectors"

    def get_queryset(self) -> QuerySet[Sector]:
        """Published sectors in admin order."""
        return Sector.objects.published()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add breadcrumbs."""
        context = super().get_context_data(**kwargs)
        crumbs = [("Home", "/"), ("Sectors", "/sectors/")]
        copy = page_copy(
            "sectors",
            "Sectors we serve",
            "Cooling failures cost different things in different buildings. We plan "
            "maintenance around what your building cannot afford to lose.",
        )
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
            }
        )
        return context


class SectorDetailView(DetailView):
    """``/sectors/<slug>/``: sector landing page with relevant services and proof."""

    template_name = "projects/sector_detail.html"
    context_object_name = "sector"

    def get_queryset(self) -> QuerySet[Sector]:
        """Published sectors with key services prefetched."""
        return Sector.objects.published().prefetch_related("key_services__category")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add case studies and breadcrumbs."""
        context = super().get_context_data(**kwargs)
        sector: Sector = context["sector"]
        crumbs = [("Home", "/"), ("Sectors", "/sectors/"), (sector.name, sector.get_absolute_url())]
        context.update(
            {
                "seo": sector,
                "case_studies": CaseStudy.objects.published().for_cards().filter(sector=sector)[:6],
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                **trust_strip_context(),
            }
        )
        return context


class CaseStudyListView(ListView):
    """``/case-studies/``: filterable by sector, service and area via query string."""

    template_name = "projects/case_study_list.html"
    context_object_name = "case_studies"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[CaseStudy]:
        """Published case studies filtered by ``?sector=``, ``?service=``, ``?area=``."""
        qs = CaseStudy.objects.published().for_cards()
        sector = self.request.GET.get("sector")
        service = self.request.GET.get("service")
        area = self.request.GET.get("area")
        if sector:
            qs = qs.filter(sector__slug=sector)
        if service:
            qs = qs.filter(services__slug=service)
        if area:
            qs = qs.filter(area__slug=area)
        return qs.distinct()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add filter options and breadcrumbs."""
        context = super().get_context_data(**kwargs)
        crumbs = [("Home", "/"), ("Case studies", "/case-studies/")]
        copy = page_copy(
            "case-studies",
            "Case studies",
            "Real sites, real faults, measurable results. Filter by sector, service or area.",
        )
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "sectors": Sector.objects.published(),
                "services": Service.objects.published().select_related("category"),
                "areas": ServiceArea.objects.published(),
                "filters": {
                    "sector": self.request.GET.get("sector", ""),
                    "service": self.request.GET.get("service", ""),
                    "area": self.request.GET.get("area", ""),
                },
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
            }
        )
        return context


class CaseStudyDetailView(DetailView):
    """``/case-studies/<slug>/``: challenge → solution → result."""

    template_name = "projects/case_study_detail.html"
    context_object_name = "case_study"

    def get_queryset(self) -> QuerySet[CaseStudy]:
        """Published case studies with all relations loaded."""
        return CaseStudy.objects.published().for_detail()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add breadcrumbs, related work and Article schema."""
        context = super().get_context_data(**kwargs)
        cs: CaseStudy = context["case_study"]
        crumbs = [
            ("Home", "/"),
            ("Case studies", "/case-studies/"),
            (cs.title, cs.get_absolute_url()),
        ]
        article = {
            "@context": schema.SCHEMA_CONTEXT,
            "@type": "Article",
            "headline": cs.title,
            "description": cs.summary,
            "datePublished": cs.published_at.date().isoformat(),
            "dateModified": cs.updated_at.date().isoformat(),
            "author": {"@id": schema.organization_id()},
            "publisher": {"@id": schema.organization_id()},
            "mainEntityOfPage": schema.absolute_url(cs.get_absolute_url()),
        }
        if cs.hero_image:
            article["image"] = schema.absolute_url(cs.hero_image.url)
        context.update(
            {
                "seo": cs,
                "related": CaseStudy.objects.published()
                .for_cards()
                .filter(sector=cs.sector)
                .exclude(pk=cs.pk)[:3],
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs), article],
                **trust_strip_context(),
            }
        )
        return context
