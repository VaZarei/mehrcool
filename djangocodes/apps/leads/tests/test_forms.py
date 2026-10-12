"""Form validation and submission tests for contact and emergency forms."""

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.leads.forms import ContactEnquiryForm, EmergencyCalloutForm
from apps.leads.models import (
    ChoiceGroup,
    ContactEnquiry,
    EmergencyCallout,
    FormFieldChoice,
    LeadStatus,
)


class EmergencyFormTests(TestCase):
    def test_phone_required_and_validated(self):
        form = EmergencyCalloutForm(data={"phone": "123"})
        self.assertFalse(form.is_valid())
        self.assertIn("full phone number", form.errors["phone"][0])

    def test_valid_with_only_phone(self):
        form = EmergencyCalloutForm(data={"phone": "07778 889080"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_honeypot_rejects_bots(self):
        form = EmergencyCalloutForm(data={"phone": "07778889080", "website_url": "http://spam"})
        self.assertFalse(form.is_valid())

    def test_issue_choices_come_from_lookup_table(self):
        FormFieldChoice.objects.create(
            group=ChoiceGroup.EMERGENCY_ISSUE, label="Cold room", value="cr"
        )
        FormFieldChoice.objects.create(
            group=ChoiceGroup.EMERGENCY_ISSUE, label="Hidden", value="h", is_active=False
        )
        form = EmergencyCalloutForm()
        labels = [c.label for c in form.fields["issue"].queryset]
        self.assertEqual(labels, ["Cold room"])


class ContactFormTests(TestCase):
    def valid_data(self, **overrides):
        data = {
            "name": "Jane Doe",
            "phone": "020 7123 4567",
            "email": "jane@example.com",
            "message": "Please quote for PPM on 12 units.",
            "consent": "on",
        }
        data.update(overrides)
        return data

    def test_valid(self):
        self.assertTrue(ContactEnquiryForm(data=self.valid_data()).is_valid())

    def test_consent_required(self):
        form = ContactEnquiryForm(data=self.valid_data(consent=""))
        self.assertFalse(form.is_valid())
        self.assertIn("consent", form.errors)

    def test_email_required(self):
        form = ContactEnquiryForm(data=self.valid_data(email=""))
        self.assertFalse(form.is_valid())


class SubmissionViewTests(TestCase):
    def test_emergency_post_stores_and_emails_and_redirects(self):
        response = self.client.post(
            reverse("leads:emergency"), {"phone": "07778889080", "postcode": "E14 9FP"}
        )
        self.assertRedirects(response, reverse("leads:emergency_thanks"))
        lead = EmergencyCallout.objects.get()
        self.assertEqual(lead.status, LeadStatus.NEW)
        self.assertEqual(lead.postcode, "E14 9FP")
        self.assertTrue(lead.source_url.endswith("/emergency-callout/"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("EMERGENCY", mail.outbox[0].subject)
        lead.refresh_from_db()
        self.assertIsNotNone(lead.notified_at)

    def test_emergency_htmx_returns_fragment_with_trigger(self):
        response = self.client.post(
            reverse("leads:emergency"), {"phone": "07778889080"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Trigger"], "lead:emergency")
        self.assertContains(response, "calling")
        self.assertNotContains(response, "<html")

    def test_emergency_htmx_invalid_returns_form_with_error(self):
        response = self.client.post(
            reverse("leads:emergency"), {"phone": "12"}, HTTP_HX_REQUEST="true"
        )
        self.assertContains(response, "field--error")
        self.assertEqual(EmergencyCallout.objects.count(), 0)

    def test_contact_post(self):
        response = self.client.post(
            reverse("leads:contact"),
            {
                "name": "Jane",
                "phone": "02071234567",
                "email": "jane@example.com",
                "message": "Hello",
                "consent": "on",
            },
        )
        self.assertRedirects(response, reverse("leads:contact_thanks"))
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        self.assertEqual(mail.outbox[0].reply_to, ["jane@example.com"])

    def test_bot_submission_not_stored(self):
        self.client.post(reverse("leads:emergency"), {"phone": "07778889080", "website_url": "x"})
        self.assertEqual(EmergencyCallout.objects.count(), 0)
