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

from .forms import ContactEnquiryForm
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






class RepairView(TemplateView):
    """``/repair/``: emergency callback and scheduled-repair forms side by side.

    Each form posts to its own existing endpoint (``leads:emergency`` /
    ``leads:request``); this view only renders the two unbound forms together.
    """

    template_name = "leads/repair.html"
    copy_slug = "repair"
    copy_default_title = "Refrigeration & air conditioning repair"
    copy_default_intro = (
        "Equipment down right now? Call the duty engineer. Planning a repair or site "
        "visit? Send the details below."
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add both unbound forms, breadcrumbs and schema."""
        context = super().get_context_data(**kwargs)
        copy = page_copy(self.copy_slug, self.copy_default_title, self.copy_default_intro)
        crumbs = [("Home", "/"), ("Repair", reverse("leads:repair"))]
        context.update(
            {
                "copy": copy,
                "seo": copy.page,
                "form": EmergencyCalloutForm(),
                "request_form": RequestEnquiryForm(),
                "breadcrumbs": crumbs,
                "schema_graph": [schema.breadcrumbs(crumbs)],
                "audience": "Emergency callers (Path A) and scheduled-repair enquirers (Path B)",
                **trust_strip_context(),
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


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import RepairRequestForm
from .models import RepairRequest

def repair_request_view(request):
    if request.method == 'POST':
        form = RepairRequestForm(request.POST, request.FILES)
        if form.is_valid():
            repair_obj = form.save(commit=False)
            symptoms = request.POST.getlist('symptoms')
            repair_obj.symptoms = symptoms
            repair_obj.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/repair-confirmation/{repair_obj.ticket_number}/'
                })
            return redirect('repair_confirmation', ticket_number=repair_obj.ticket_number)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)

    form = RepairRequestForm()
    return render(request, 'leads/repair_request_wizard.html', {'form': form})

def repair_confirmation_view(request, ticket_number):
    repair_request = get_object_or_404(RepairRequest, ticket_number=ticket_number)
    template = 'leads/repair_confirmation_emergency.html' if repair_request.urgency == 'EMERGENCY' else 'leads/repair_confirmation_standard.html'
    return render(request, template, {'request_data': repair_request})