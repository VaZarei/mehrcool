"""Views for the contact page, emergency page and their form submissions.

Both forms work without JavaScript (full-page POST → redirect → thank-you). With HTMX
present, the same views return just the form/confirmation fragment.
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from apps.core.models import SiteSettings
from apps.core.views import trust_strip_context
from apps.locations.models import ServiceArea
from apps.pages.services import page_copy
from apps.seo import schema

from .forms import ContactEnquiryForm, RequestEnquiryForm, EmergencyCalloutForm
from .services import attach_request_metadata, notify_new_lead

HX_REQUEST_HEADER = "HX-Request"


def is_htmx(request: HttpRequest) -> bool:
    """Whether the request was made by HTMX.

    Args:
        request: Current request.

    Returns:
        ``True`` when the ``HX-Request`` header is present.
    """
    return request.headers.get(HX_REQUEST_HEADER) == "true"


class LeadFormView(FormView):
    """Shared behaviour: store, notify, respond with fragment or redirect."""

    email_template = ""
    fragment_template = ""
    success_fragment_template = ""
    success_url_name = ""
    event_name = ""
    copy_slug = ""
    copy_default_title = ""
    copy_default_intro = ""

    def get_copy(self) -> Any:
        """Admin-editable heading/intro for this page.

        Returns:
            A ``PageCopy`` instance.
        """
        return page_copy(self.copy_slug, self.copy_default_title, self.copy_default_intro)

    def form_valid(self, form: Any) -> HttpResponse:
        """Persist the lead, send the notification and respond.

        Args:
            form: The valid bound form.

        Returns:
            Fragment (HTMX) or redirect (plain HTML).
        """
        lead = form.save(commit=False)
        attach_request_metadata(lead, self.request)
        lead.save()
        notify_new_lead(lead, self.email_template)
        if is_htmx(self.request):
            response = render(
                self.request, self.success_fragment_template, {"lead": lead, **self.extra()}
            )
            response["HX-Trigger"] = self.event_name
            return response
        return redirect(reverse(self.success_url_name))

    def form_invalid(self, form: Any) -> HttpResponse:
        """Re-render just the form for HTMX, or the whole page otherwise."""
        if is_htmx(self.request):
            return render(self.request, self.fragment_template, {"form": form, **self.extra()})
        return super().form_invalid(form)

    def extra(self) -> dict[str, Any]:
        """Extra context for HTMX fragments: the editable page copy."""
        return {"copy": self.get_copy()}


class ContactView(LeadFormView):
    """``/contact/``: form, map, hours and direct lines (Path B)."""

    template_name = "leads/contact.html"
    form_class = ContactEnquiryForm
    email_template = "leads/email/contact_enquiry.txt"
    fragment_template = "leads/partials/contact_form.html"
    success_fragment_template = "leads/partials/contact_success.html"
    success_url_name = "leads:contact_thanks"
    event_name = "lead:contact"
    copy_slug = "contact"
    copy_default_title = "Contact Mehr Cool"
    copy_default_intro = (
        "For a breakdown, call — we answer around the clock. For maintenance contracts, "
        "installations and tenders, send the site details and an engineer will reply within "
        "one working day."
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add breadcrumbs, map and schema."""
        context = super().get_context_data(**kwargs)
        crumbs = [("Home", "/"), ("Contact", reverse("leads:contact"))]
        copy = self.get_copy()
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                "audience": "Contract buyers (Path B); emergency callers routed to phone",
                **trust_strip_context(),
            }
        )
        return context

class RequestView(LeadFormView):
    """``/Request/``: form, map, hours and direct lines (Path B)."""

    template_name = "leads/request.html"
    form_class = RequestEnquiryForm
    email_template = "leads/email/request_enquiry.txt"
    fragment_template = "leads/partials/request_form.html"
    success_fragment_template = "leads/partials/request_success.html"
    success_url_name = "leads:request_thanks"
    event_name = "lead:request"
    copy_slug = "request"
    copy_default_title = "request form MehrCool"
    copy_default_intro = (
        "For a breakdown, call — we answer around the clock. For maintenance contracts, "
        "installations and tenders, send the site details and an engineer will reply within "
        "one working day."
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add breadcrumbs, map and schema."""
        context = super().get_context_data(**kwargs)
        crumbs = [("Home", "/"), ("Contact", reverse("leads:contact"))]
        copy = self.get_copy()
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                "audience": "Contract buyers (Path B); emergency callers routed to phone",
                **trust_strip_context(),
            }
        )
        return context


class EmergencyView(LeadFormView):
    """``/emergency-callout/``: phone dominant, one-field callback (Path A)."""

    template_name = "leads/emergency.html"
    form_class = EmergencyCalloutForm
    email_template = "leads/email/emergency_callout.txt"
    fragment_template = "leads/partials/emergency_form.html"
    success_fragment_template = "leads/partials/emergency_success.html"
    success_url_name = "leads:emergency_thanks"
    event_name = "lead:emergency"
    copy_slug = "emergency-callout"
    copy_default_title = "Refrigeration or air conditioning down? Call now."
    copy_default_intro = (
        "Leave your mobile number and the duty engineer rings you back within minutes."
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add coverage areas and schema; deliberately no trust strip or heavy media."""
        context = super().get_context_data(**kwargs)
        crumbs = [("Home", "/"), ("Emergency callout", reverse("leads:emergency"))]
        copy = self.get_copy()
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "areas": ServiceArea.objects.published().only("name", "slug", "region")[:24],
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                "audience": "Emergency callers (Path A)",
                "minimal_chrome": True,
            }
        )
        return context


class ThanksView(TemplateView):
    """Generic thank-you page (noindex) shown after a non-JS submission."""

    template_name = "leads/thanks.html"
    heading = "Thanks — we've got your message"
    body = ""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add heading/body and mark the page noindex."""
        context = super().get_context_data(**kwargs)
        context.update({"heading": self.heading, "body": self.body, "noindex": True})
        return context


class ContactThanksView(ThanksView):
    """Thank-you after a contact enquiry."""

    heading = "Thanks — we've received your enquiry"
    body = "An engineer will reply within one working day. If it's urgent, call us now."

class RequestThanksView(ThanksView):
    """Thank-you after a contact enquiry."""

    heading = "Thanks — we've received your enquiry"
    body = "An engineer will reply within one working day. If it's urgent, call us now."


class EmergencyThanksView(ThanksView):
    """Thank-you after an emergency callback request."""

    heading = "We're calling you back"
    body = "Keep your phone to hand. The duty engineer will ring you within minutes."

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Keep the emergency page's minimal chrome."""
        context = super().get_context_data(**kwargs)
        context["minimal_chrome"] = True
        context["site"] = SiteSettings.load()
        return context
