"""Model tests: singleton behaviour, derived helpers, navigation resolution."""

from django.core.cache import cache
from django.test import TestCase

from apps.core.constants import SITE_SETTINGS_PK
from apps.core.models import IntentCard, LinkTarget, NavigationItem, SiteSettings, TrustBadge
from apps.core.models.settings import normalise_phone_for_href
from apps.services.models import ServiceCategory


class SiteSettingsTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_load_creates_singleton_with_pk_one(self):
        site = SiteSettings.load()
        self.assertEqual(site.pk, SITE_SETTINGS_PK)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_save_forces_pk_one(self):
        other = SiteSettings(trading_name="Other")
        other.pk = 99
        other.save()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.objects.get().trading_name, "Other")

    def test_delete_is_ignored(self):
        site = SiteSettings.load()
        site.delete()
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_tel_and_whatsapp_links(self):
        site = SiteSettings.load()
        site.emergency_phone = "+44 77 7888 9080"
        site.whatsapp_number = "+44 77 7888 9080"
        site.whatsapp_prefill_message = "Hi there"
        self.assertEqual(site.emergency_tel_href, "tel:+447778889080")
        self.assertEqual(site.whatsapp_href, "https://wa.me/447778889080?text=Hi%20there")

    def test_whatsapp_hidden_when_blank(self):
        site = SiteSettings.load()
        site.whatsapp_number = ""
        self.assertEqual(site.whatsapp_href, "")

    def test_list_helpers(self):
        site = SiteSettings.load()
        site.areas_served = "London, Greater London , Berkshire"
        site.cta_band_checklist = "One\n\nTwo\n"
        site.home_why_items = "Title :: Body"
        self.assertEqual(site.areas_served_list, ["London", "Greater London", "Berkshire"])
        self.assertEqual(site.cta_checklist, ["One", "Two"])
        self.assertEqual(site.why_items[0]["title"], "Title")

    def test_normalise_phone(self):
        self.assertEqual(normalise_phone_for_href("0207 123 4567"), "02071234567")
        self.assertEqual(normalise_phone_for_href("+44 (0)20 7123"), "+440207123")


class NavigationItemTests(TestCase):
    def test_url_target(self):
        item = NavigationItem(label="Contact", target_type=LinkTarget.URL, url="/contact/")
        self.assertEqual(item.get_url(), "/contact/")
        self.assertFalse(item.is_external)

    def test_category_target(self):
        cat = ServiceCategory.objects.create(name="AC", slug="ac", intro="x")
        item = NavigationItem(
            label="AC", target_type=LinkTarget.SERVICE_CATEGORY, service_category=cat
        )
        self.assertEqual(item.get_url(), "/ac/")

    def test_heading_only(self):
        item = NavigationItem(label="Company", target_type=LinkTarget.NONE)
        self.assertEqual(item.get_url(), "")

    def test_external(self):
        item = NavigationItem(label="X", target_type=LinkTarget.URL, url="https://example.com")
        self.assertTrue(item.is_external)


class TrustBadgeTests(TestCase):
    def test_badges_default_inactive(self):
        badge = TrustBadge(name="REFCOM", logo="x.svg")
        self.assertFalse(badge.is_active)
        self.assertEqual(badge.alt, "REFCOM")

    def test_intent_card_str(self):
        self.assertEqual(str(IntentCard(label="Repair")), "Repair")
