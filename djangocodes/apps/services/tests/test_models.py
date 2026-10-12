"""Model tests for services, categories and publishing."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.core.models import PublishStatus
from apps.services.models import Service, ServiceCategory


class ServiceModelTests(TestCase):
    def setUp(self):
        self.cat = ServiceCategory.objects.create(
            name="Commercial Refrigeration",
            slug="commercial-refrigeration",
            intro="x",
            status=PublishStatus.PUBLISHED,
        )

    def test_flat_keyword_urls(self):
        service = Service.objects.create(
            category=self.cat,
            name="Walk-In Cold Rooms",
            slug="walk-in-cold-rooms",
            short_summary="s",
        )
        self.assertEqual(self.cat.get_absolute_url(), "/commercial-refrigeration/")
        self.assertEqual(
            service.get_absolute_url(), "/commercial-refrigeration/walk-in-cold-rooms/"
        )

    def test_published_filter_respects_status_and_date(self):
        Service.objects.create(category=self.cat, name="Draft", slug="d", short_summary="s")
        Service.objects.create(
            category=self.cat,
            name="Future",
            slug="f",
            short_summary="s",
            status=PublishStatus.PUBLISHED,
            published_at=timezone.now() + timedelta(days=1),
        )
        live = Service.objects.create(
            category=self.cat,
            name="Live",
            slug="l",
            short_summary="s",
            status=PublishStatus.PUBLISHED,
        )
        self.assertEqual(list(Service.objects.published()), [live])
        self.assertTrue(live.is_published)

    def test_unpublished_service_404s(self):
        Service.objects.create(category=self.cat, name="Draft", slug="d", short_summary="s")
        self.assertEqual(self.client.get("/commercial-refrigeration/d/").status_code, 404)

    def test_category_prefetch_attribute(self):
        Service.objects.create(
            category=self.cat,
            name="Live",
            slug="l",
            short_summary="s",
            status=PublishStatus.PUBLISHED,
        )
        cat = ServiceCategory.objects.published().with_published_services().get()
        self.assertEqual(len(cat.published_services), 1)

    def test_slug_dispatch_prefers_category_then_page(self):
        from apps.pages.models import Page

        Page.objects.create(title="About", slug="about", status=PublishStatus.PUBLISHED)
        self.assertEqual(self.client.get("/about/").status_code, 200)
        self.assertEqual(self.client.get("/commercial-refrigeration/").status_code, 200)
        self.assertEqual(self.client.get("/missing/").status_code, 404)
