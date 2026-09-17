"""Lead business logic: request metadata capture, notification emails, CSV export."""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterable
from typing import Any

from django.core.mail import EmailMessage
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.models import SiteSettings

from .models import LeadBase

logger = logging.getLogger(__name__)


def attach_request_metadata(lead: LeadBase, request: HttpRequest) -> None:
    """Record where the lead came from before saving.

    Args:
        lead: Unsaved lead instance.
        request: The submitting request.
    """
    lead.source_url = request.build_absolute_uri()[:300]
    lead.referrer = request.headers.get("Referer", "")[:300]
    lead.user_agent = request.headers.get("User-Agent", "")[:300]


def notify_new_lead(lead: LeadBase, template: str) -> bool:
    """Email the configured recipient about a new lead.

    Args:
        lead: Saved lead.
        template: Text template path rendering the email body.

    Returns:
        ``True`` if the email was sent.
    """
    site = SiteSettings.load()
    body = render_to_string(template, {"lead": lead, "site": site})
    message = EmailMessage(
        subject=lead.notification_subject(),
        body=body,
        to=[site.notification_recipient],
        reply_to=[lead.email] if lead.email else None,
    )
    try:
        sent = message.send(fail_silently=False)
    except Exception:  # noqa: BLE001 - never let email failure lose a stored lead
        logger.exception("Lead notification failed for %s #%s", type(lead).__name__, lead.pk)
        return False
    if sent:
        type(lead).objects.filter(pk=lead.pk).update(notified_at=timezone.now())
    return bool(sent)


def export_csv(queryset: Iterable[models.Model], fields: list[str], filename: str) -> HttpResponse:
    """Stream a queryset as CSV for the admin export action.

    Args:
        queryset: Rows to export.
        fields: Attribute names to include, in order.
        filename: Download filename.

    Returns:
        ``text/csv`` response.
    """
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([_cell(obj, f) for f in fields])
    return response


def _cell(obj: Any, field: str) -> str:
    """Resolve a field (supporting ``get_<field>_display``) to a CSV-safe string.

    Args:
        obj: Model instance.
        field: Attribute name.

    Returns:
        String value.
    """
    display = getattr(obj, f"get_{field}_display", None)
    value = display() if callable(display) else getattr(obj, field, "")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return "" if value is None else str(value)
