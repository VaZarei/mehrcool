"""Tests for schema builders and the pages text renderer."""

from decimal import Decimal

from django.test import TestCase

from apps.core.models import SiteSettings
from apps.pages.services import parse_block_items, render_text
from apps.seo import schema


class SchemaTests(TestCase):
    def test_aggregate_rating_none_without_reviews(self):
        self.assertIsNone(schema.aggregate_rating(None, 0))
        self.assertIsNone(schema.aggregate_rating(Decimal("4.9"), 0))

    def test_aggregate_rating_formats(self):
        data = schema.aggregate_rating(Decimal("4.86"), 12)
        self.assertEqual(data["ratingValue"], "4.9")
        self.assertEqual(data["reviewCount"], "12")

    def test_breadcrumbs(self):
        data = schema.breadcrumbs([("Home", "/"), ("Contact", "/contact/")])
        self.assertEqual(data["itemListElement"][1]["position"], 2)
        self.assertTrue(data["itemListElement"][1]["item"].endswith("/contact/"))

    def test_local_business_core_fields(self):
        site = SiteSettings.load()
        site.company_number = "15733975"
        data = schema.local_business(site, [], None, 0)
        self.assertEqual(data["telephone"], "+44-77-7888-9080")
        self.assertEqual(data["address"]["postalCode"], "E14 9FP")
        self.assertEqual(data["priceRange"], "$$$")
        self.assertEqual(len(data["openingHoursSpecification"][0]["dayOfWeek"]), 7)
        self.assertEqual(data["areaServed"][0], {"@type": "City", "name": "London"})
        self.assertNotIn("aggregateRating", data)

    def test_faq_page_empty(self):
        self.assertIsNone(schema.faq_page([]))


class TextRenderTests(TestCase):
    def test_paragraphs_and_lists(self):
        html = render_text(
            "First **bold** line\n\n- item one\n- item two\n\n## Sub\nText [link](/x/)"
        )
        self.assertIn("<p>First <strong>bold</strong> line</p>", html)
        self.assertIn("<ul>\n<li>item one</li>\n<li>item two</li>\n</ul>", html)
        self.assertIn("<h3>Sub</h3>", html)
        self.assertIn('<a href="/x/">link</a>', html)

    def test_escapes_html(self):
        self.assertIn("&lt;script&gt;", render_text("<script>alert(1)</script>"))

    def test_parse_items(self):
        items = parse_block_items("A :: B :: /c/\nOnly title\n\n")
        self.assertEqual(items[0], {"title": "A", "body": "B", "url": "/c/"})
        self.assertEqual(items[1], {"title": "Only title", "body": "", "url": ""})
        self.assertEqual(len(items), 2)
