"""XML sitemaps covering every published object."""

from __future__ import annotations

from typing import Any

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet
from django.urls import reverse

from apps.locations.models import ServiceArea
from apps.pages.models import Page
from apps.projects.models import CaseStudy, Sector
from apps.services.models import Service, ServiceCategory


class StaticViewSitemap(Sitemap):
    """Hand-built pages that are not database objects."""

    protocol = "https"
    changefreq = "monthly"

    def items(self) -> list[str]:
        """URL names of static views.

        Returns:
            List of reversible names.
        """
        return [
            "core:home",
            "services:index",
            "leads:contact",
            "leads:emergency",
            "projects:sector_list",
            "projects:case_study_list",
            "locations:index",
        ]

    def location(self, item: str) -> str:
        """Reverse the URL name."""
        return reverse(item)

    def priority(self, item: str) -> float:
        """Homepage and emergency page rank highest."""
        return 1.0 if item in ("core:home", "leads:emergency") else 0.7


class PublishedSitemap(Sitemap):
    """Base for models using ``PublishableModel``."""

    protocol = "https"
    changefreq = "monthly"
    priority = 0.6
    model: Any = None

    def items(self) -> QuerySet[Any]:
        """Published rows not flagged noindex."""
        return self.model.objects.published().filter(noindex=False)

    def lastmod(self, obj: Any) -> Any:
        """Last modification timestamp."""
        return obj.updated_at


class ServiceCategorySitemap(PublishedSitemap):
    """Category hubs."""

    model = ServiceCategory
    priority = 0.9


class ServiceSitemap(PublishedSitemap):
    """Individual services."""

    model = Service
    priority = 0.8

    def items(self) -> QuerySet[Service]:
        """Published services with category joined for URL building."""
        return super().items().select_related("category")


class PageSitemap(PublishedSitemap):
    """Content pages (excluding the reserved copy-holder pages for index views)."""

    model = Page
    priority = 0.5

    def items(self) -> QuerySet[Page]:
        """Published pages that are actually served at ``/<slug>/``."""
        from apps.pages.services import RESERVED_PAGE_SLUGS

        return super().items().exclude(slug__in=RESERVED_PAGE_SLUGS)


class SectorSitemap(PublishedSitemap):
    """Sector landing pages."""

    model = Sector
    priority = 0.7


class CaseStudySitemap(PublishedSitemap):
    """Case studies."""

    model = CaseStudy
    priority = 0.6


class ServiceAreaSitemap(PublishedSitemap):
    """Borough landing pages."""

    model = ServiceArea
    priority = 0.7


SITEMAPS = {
    "static": StaticViewSitemap,
    "categories": ServiceCategorySitemap,
    "services": ServiceSitemap,
    "pages": PageSitemap,
    "sectors": SectorSitemap,
    "case-studies": CaseStudySitemap,
    "areas": ServiceAreaSitemap,
}
