"""Lead business logic: request metadata capture, notification emails, CSV export."""

from __future__ import annotations

import csv
import logging
import re
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from email.utils import parseaddr
from typing import Any

from django.core.mail import EmailMessage
from django.db import close_old_connections, connection, models, transaction
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.models import SiteSettings

from .models import LeadBase

logger = logging.getLogger(__name__)

_email_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="lead-email")


def _extract_email_address(email_string: str) -> str:
    """Extract email address from formatted string like 'Name <email@example.com>'."""
    _, addr = parseaddr(email_string)
    return addr or email_string


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
    from django.conf import settings

    site = SiteSettings.load()
    body = render_to_string(template, {"lead": lead, "site": site, "SITE_URL": settings.SITE_URL})
    message = EmailMessage(
        subject=lead.notification_subject(),
        body=body,
        from_email=_extract_email_address(settings.DEFAULT_FROM_EMAIL),
        to=[site.notification_recipient],
        reply_to=[lead.email] if lead.email else None,
    )
    if template.endswith('.html'):
        message.content_subtype = "html"
    try:
        sent = message.send(fail_silently=False)
    except Exception:  # noqa: BLE001 - never let email failure lose a stored lead
        logger.exception("Lead notification failed for %s #%s", type(lead).__name__, lead.pk)
        return False
    if sent:
        type(lead).objects.filter(pk=lead.pk).update(notified_at=timezone.now())
    return bool(sent)


def send_customer_confirmation(lead: LeadBase, template: str) -> bool:
    """Email the customer a confirmation of their submission.

    Args:
        lead: Saved lead.
        template: Text template path rendering the email body.

    Returns:
        ``True`` if the email was sent.
    """
    if not lead.email:
        logger.warning("No email address for %s #%s", type(lead).__name__, lead.pk)
        return False

    from django.conf import settings

    site = SiteSettings.load()
    body = render_to_string(template, {"lead": lead, "site": site, "SITE_URL": settings.SITE_URL})
    from_email = _extract_email_address(settings.DEFAULT_FROM_EMAIL)
    logger.info("Sending customer confirmation for %s #%s", type(lead).__name__, lead.pk)
    message = EmailMessage(
        subject=f"Thanks for getting in touch — {site.trading_name}",
        body=body,
        from_email=from_email,
        to=[lead.email],
    )
    message.content_subtype = "html"
    try:
        sent = message.send(fail_silently=False)
        logger.info("Customer confirmation sent successfully: %s", bool(sent))
    except Exception as e:
        # No traceback/message: SMTP errors embed the recipient address.
        logger.error("Customer confirmation failed for %s #%s: %s", type(lead).__name__, lead.pk, type(e).__name__)
        return False
    return bool(sent)


def send_repair_confirmation(repair: Any) -> bool:
    """Email the customer a confirmation of their repair request.

    Args:
        repair: Saved ``RepairRequest``.

    Returns:
        ``True`` if the email was sent.
    """
    if not repair.email:
        logger.info("No email on repair request %s; skipping confirmation", repair.ticket_number)
        return False

    from django.conf import settings

    site = SiteSettings.load()
    body = render_to_string("leads/email/repair_confirmation.html", {"repair": repair, "site": site, "SITE_URL": settings.SITE_URL})
    kind = "Emergency repair request" if repair.urgency == "EMERGENCY" else "Repair booking request"
    message = EmailMessage(
        subject=f"{kind} received ({repair.ticket_number}) — {site.trading_name}",
        body=body,
        from_email=_extract_email_address(settings.DEFAULT_FROM_EMAIL),
        to=[repair.email],
    )
    message.content_subtype = "html"
    try:
        sent = message.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001 - never let email failure affect the stored request
        logger.error("Repair confirmation failed for %s: %s", repair.ticket_number, type(exc).__name__)
        return False
    return bool(sent)


def notify_staff_repair(repair: Any) -> bool:
    """Email the configured staff recipient about a new repair request.

    Args:
        repair: Saved ``RepairRequest``.

    Returns:
        ``True`` if the email was sent.
    """
    from django.conf import settings

    site = SiteSettings.load()
    body = render_to_string("leads/email/repair_staff_notification.html", {"repair": repair, "site": site, "SITE_URL": settings.SITE_URL})
    prefix = "EMERGENCY repair" if repair.urgency == "EMERGENCY" else "Repair request"
    message = EmailMessage(
        subject=f"{prefix} {repair.ticket_number} — {repair.full_name}",
        body=body,
        from_email=_extract_email_address(settings.DEFAULT_FROM_EMAIL),
        to=[site.notification_recipient],
        reply_to=[repair.email] if repair.email else None,
    )
    message.content_subtype = "html"
    try:
        sent = message.send(fail_silently=False)
    except Exception:  # noqa: BLE001 - never let email failure affect the stored request
        logger.exception("Repair staff notification failed for %s", repair.ticket_number)
        return False
    return bool(sent)


def dispatch_repair_confirmation(repair: Any) -> None:
    """Queue staff notification and customer confirmation in parallel, after commit."""

    def queue() -> None:
        _run_in_background(notify_staff_repair, repair)
        _run_in_background(send_repair_confirmation, repair)

    transaction.on_commit(queue)


def _run_in_background(func: Any, *args: Any) -> None:
    """Run ``func`` on the email pool, releasing its DB connection afterwards."""

    def runner() -> None:
        close_old_connections()
        try:
            func(*args)
        except Exception:  # noqa: BLE001 - background task must never raise
            logger.exception("Background email task %s failed", func.__name__)
        finally:
            connection.close()

    _email_executor.submit(runner)


def dispatch_lead_emails(lead: LeadBase, notify_template: str, customer_template: str = "") -> None:
    """Send the staff notification and customer confirmation in parallel, off-request.

    Both emails are queued once the lead's transaction commits, so the HTTP
    response returns immediately and failures are only logged.

    Args:
        lead: Saved lead.
        notify_template: Template for the staff notification.
        customer_template: Template for the customer confirmation (optional).
    """

    def queue() -> None:
        _run_in_background(notify_new_lead, lead, notify_template)
        if customer_template:
            _run_in_background(send_customer_confirmation, lead, customer_template)

    transaction.on_commit(queue)


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
    return "" if value is None else _csv_safe(str(value))


_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
_INTL_PHONE = re.compile(r"^\+[\d\s().-]{7,}$")


def _csv_safe(text: str) -> str:
    """Neutralise spreadsheet formulas by prefixing a quote (CSV/formula injection).

    Genuine international phone numbers (``+44 20 ...``) are left untouched.
    """
    if text.startswith(_FORMULA_PREFIXES) and not _INTL_PHONE.match(text):
        return "'" + text
    return text
