"""View smoke tests for every public URL, plus the 'no hard-coded contact details' guard."""

import json
import re
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import SiteSettings
from apps.locations.models import ServiceArea
from apps.pages.models import Page
from apps.pages.services import RESERVED_PAGE_SLUGS
from apps.projects.models import CaseStudy, Sector
from apps.services.models import Service, ServiceCategory

# Values that must only ever come from SiteSettings.
FORBIDDEN_LITERALS = [
    "7888 9080",
    "447778889080",
    "info@mehrcoolrefrigeration.co.uk",
    "East Ferry Road",
    "E14 9FP",
    "15733975",
]


class SeededSiteTestCase(TestCase):
    """Loads the demo seed once so view tests run against realistic content."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", "--skip-groups", verbosity=0)
        cache.clear()


@override_settings(STYLEGUIDE_ENABLED=True, DEBUG=False)
class PublicUrlSmokeTests(SeededSiteTestCase):
    def all_public_urls(self):
        urls = [
            "/",
            reverse("services:index"),
            reverse("leads:contact"),
            reverse("leads:emergency"),
            reverse("leads:contact_thanks"),
            reverse("leads:emergency_thanks"),
            reverse("projects:sector_list"),
            reverse("projects:case_study_list"),
            reverse("projects:case_study_list") + "?sector=restaurants&service=freezer-rooms",
            reverse("locations:index"),
            reverse("core:styleguide"),
            reverse("core:vcard"),
            reverse("core:vcard_qr"),
            "/robots.txt",
            "/sitemap.xml",
        ]
        urls += [c.get_absolute_url() for c in ServiceCategory.objects.all()]
        urls += [s.get_absolute_url() for s in Service.objects.select_related("category")]
        urls += [s.get_absolute_url() for s in Sector.objects.all()]
        urls += [c.get_absolute_url() for c in CaseStudy.objects.all()]
        urls += [a.get_absolute_url() for a in ServiceArea.objects.all()]
        urls += [p.get_absolute_url() for p in Page.objects.exclude(slug__in=RESERVED_PAGE_SLUGS)]
        return urls

    def test_every_public_url_returns_200(self):
        for url in self.all_public_urls():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, url)

    def test_quote_redirects(self):
        self.assertEqual(self.client.get("/quote/").status_code, 302)

    def test_404_is_branded_with_phone(self):
        response = self.client.get("/nothing-here/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, SiteSettings.load().emergency_phone, status_code=404)

    def test_every_page_has_one_h1_and_tap_to_call(self):
        site = SiteSettings.load()
        for url in self.all_public_urls():
            if url.endswith((".xml", ".txt", ".vcf", ".svg")):
                continue
            with self.subTest(url=url):
                html = self.client.get(url).content.decode()
                self.assertEqual(len(re.findall(r"<h1[\s>]", html)), 1, f"{url} h1 count")
                self.assertIn(site.emergency_tel_href, html)

    def test_homepage_json_ld(self):
        html = self.client.get("/").content.decode()
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertTrue(scripts)
        business = json.loads(scripts[0])
        self.assertEqual(business["@type"], ["HVACBusiness", "LocalBusiness"])
        self.assertEqual(business["identifier"], "15733975")
        self.assertEqual(business["openingHoursSpecification"][0]["opens"], "00:00")
        self.assertIn("F-Gas Regulation (EC 517/2014)", business["knowsAbout"])
        self.assertTrue(business["hasOfferCatalog"]["itemListElement"])
        self.assertIn("aggregateRating", business)

    def test_service_page_has_service_and_faq_schema(self):
        service = Service.objects.filter(faqs__isnull=False).select_related("category").first()
        html = self.client.get(service.get_absolute_url()).content.decode()
        self.assertIn('"@type":"Service"', html)
        self.assertIn('"@type":"FAQPage"', html)
        self.assertIn('"@type":"BreadcrumbList"', html)

    def test_sitemap_lists_services_and_areas(self):
        xml = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("/commercial-refrigeration/walk-in-cold-rooms/", xml)
        self.assertIn("/areas/air-conditioning-refrigeration-canary-wharf/", xml)
        self.assertNotIn("<loc>https://mehrcoolrefrigeration.co.uk/services/</loc>\n<loc>", xml)

    def test_robots_points_to_sitemap(self):
        text = self.client.get("/robots.txt").content.decode()
        self.assertIn(f"Sitemap: {settings.SITE_URL}/sitemap.xml", text)
        self.assertIn("Disallow: /admin/", text)

    def test_styleguide_hidden_when_disabled(self):
        with override_settings(STYLEGUIDE_ENABLED=False):
            self.assertEqual(self.client.get(reverse("core:styleguide")).status_code, 404)

    def test_emergency_page_uses_minimal_chrome(self):
        html = self.client.get(reverse("leads:emergency")).content.decode()
        self.assertNotIn('class="nav"', html)
        self.assertNotIn("site-footer", html)

    def test_changing_phone_in_settings_updates_every_page(self):
        site = SiteSettings.load()
        site.emergency_phone = "+44 20 0000 1234"
        site.save()
        cache.clear()
        for url in ("/", reverse("leads:contact"), reverse("leads:emergency")):
            html = self.client.get(url).content.decode()
            self.assertIn("tel:+442000001234", html)

    def test_vcard_contains_settings_phone(self):
        text = self.client.get(reverse("core:vcard")).content.decode()
        self.assertIn("BEGIN:VCARD", text)
        self.assertIn("TEL;TYPE=CELL,VOICE:+447778889080", text)


class NoHardcodedContactDetailsTests(TestCase):
    """Templates must never contain the phone, email, address or company number."""

    def test_templates_have_no_literal_contact_details(self):
        template_root = Path(settings.BASE_DIR) / "templates"
        offenders = []
        for path in template_root.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for literal in FORBIDDEN_LITERALS:
                if literal in text:
                    offenders.append(f"{path.relative_to(settings.BASE_DIR)} contains {literal!r}")
        self.assertEqual(offenders, [])

    def test_templates_have_no_inline_styles_or_important(self):
        template_root = Path(settings.BASE_DIR) / "templates"
        offenders = [
            str(p.relative_to(settings.BASE_DIR))
            for p in template_root.rglob("*.html")
            if "admin" not in p.parts and " style=" in p.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])
        css_root = Path(settings.BASE_DIR) / "static" / "css"
        important = [
            str(p.relative_to(settings.BASE_DIR))
            for p in css_root.rglob("*.css")
            if not p.name.endswith(".min.css") and "!important" in p.read_text(encoding="utf-8")
        ]
        self.assertEqual(important, [])

    def test_orange_only_in_button_and_emergency_components(self):
        """The action colour token may only be referenced by primary-action components."""
        css_root = Path(settings.BASE_DIR) / "static" / "css"
        allowed = {
            "01-tokens.css",
            "button.css",
            "emergency.css",
            "intent-strip.css",
            "contact-card.css",
            "styleguide.css",
        }
        offenders = [
            p.name
            for p in css_root.rglob("*.css")
            if not p.name.endswith(".min.css")
            and p.name not in allowed
            and re.search(r"var\(--action\)|#f29d12", p.read_text(encoding="utf-8"), re.I)
        ]
        self.assertEqual(offenders, [])
