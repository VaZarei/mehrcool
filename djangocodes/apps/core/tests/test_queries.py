"""Query-count guards: listing pages must not scale queries with content (no N+1)."""

from django.core.cache import cache
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext


@override_settings(DEBUG=False)
class QueryBudgetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", "--skip-groups", verbosity=0)

    def setUp(self):
        cache.clear()

    def assert_query_budget(self, url: str, limit: int) -> None:
        """Render once to warm renditions/caches, then assert the second render is cheap."""
        self.client.get(url)
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertLess(
            len(ctx.captured_queries),
            limit,
            "\n".join(q["sql"][:140] for q in ctx.captured_queries),
        )

    def test_homepage_query_budget(self):
        self.assert_query_budget("/", 18)

    def test_services_index_budget(self):
        self.assert_query_budget("/services/", 12)

    def test_service_detail_budget(self):
        self.assert_query_budget("/commercial-refrigeration/walk-in-cold-rooms/", 22)

    def test_case_study_list_budget(self):
        self.assert_query_budget("/case-studies/", 14)

    def test_area_detail_budget(self):
        self.assert_query_budget("/areas/air-conditioning-refrigeration-canary-wharf/", 18)
