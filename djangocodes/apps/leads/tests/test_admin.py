"""Admin tests: CSV export and status actions for leads."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.leads.models import EmergencyCallout, LeadStatus


class LeadAdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "a@b.com", "pw")
        self.client.force_login(self.admin)
        self.lead = EmergencyCallout.objects.create(phone="07778889080", postcode="E14")

    def test_csv_export(self):
        url = reverse("admin:leads_emergencycallout_changelist")
        response = self.client.post(
            url, {"action": "export_as_csv", "_selected_action": [self.lead.pk]}
        )
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        body = response.content.decode()
        self.assertIn("phone", body.splitlines()[0])
        self.assertIn("07778889080", body)

    def test_mark_contacted(self):
        url = reverse("admin:leads_emergencycallout_changelist")
        self.client.post(url, {"action": "mark_contacted", "_selected_action": [self.lead.pk]})
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, LeadStatus.CONTACTED)

    def test_site_settings_changelist_redirects_to_form(self):
        response = self.client.get(reverse("admin:core_sitesettings_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/change/", response["Location"])
