"""Lead admin: pipeline filters, internal notes, CSV export and status actions."""

from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import ContactEnquiry, EmergencyCallout, FormFieldChoice, LeadNote, LeadStatus
from .services import export_csv


class LeadNoteInline(GenericTabularInline):
    """Internal notes attached to a lead."""

    model = LeadNote
    extra = 1
    fields = ("note", "author_display", "created_at")
    readonly_fields = ("author_display", "created_at")

    @admin.display(description="By")
    def author_display(self, obj: LeadNote) -> str:
        """Author username."""
        return obj.author.get_username() if obj.author_id else "—"


class LeadAdminBase(admin.ModelAdmin):
    """Shared list/filter/export behaviour for every lead type."""

    inlines = (LeadNoteInline,)
    list_filter = ("status", "created_at", "consent")
    date_hierarchy = "created_at"
    readonly_fields = (
        "created_at",
        "updated_at",
        "notified_at",
        "source_url",
        "referrer",
        "user_agent",
    )
    actions = ("export_as_csv", "mark_contacted", "mark_quoted", "mark_won", "mark_lost")
    csv_fields: list[str] = []
    list_per_page = 50

    def save_formset(self, request: HttpRequest, form: Any, formset: Any, change: bool) -> None:
        """Stamp the current user on new notes."""
        for obj in formset.save(commit=False):
            if isinstance(obj, LeadNote) and obj.author_id is None:
                obj.author = request.user
            obj.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()

    @admin.action(description="Export selected to CSV")
    def export_as_csv(self, request: HttpRequest, queryset: QuerySet[Any]) -> HttpResponse:
        """Download the selection as a spreadsheet."""
        name = f"{self.model._meta.model_name}-{timezone.now():%Y-%m-%d}.csv"
        return export_csv(queryset, self.csv_fields, name)

    def _set_status(self, queryset: QuerySet[Any], status: str) -> None:
        queryset.update(status=status)

    @admin.action(description="Mark as Contacted")
    def mark_contacted(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        """Bulk status change."""
        self._set_status(queryset, LeadStatus.CONTACTED)

    @admin.action(description="Mark as Quoted")
    def mark_quoted(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        """Bulk status change."""
        self._set_status(queryset, LeadStatus.QUOTED)

    @admin.action(description="Mark as Won")
    def mark_won(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        """Bulk status change."""
        self._set_status(queryset, LeadStatus.WON)

    @admin.action(description="Mark as Lost")
    def mark_lost(self, request: HttpRequest, queryset: QuerySet[Any]) -> None:
        """Bulk status change."""
        self._set_status(queryset, LeadStatus.LOST)


@admin.register(EmergencyCallout)
class EmergencyCalloutAdmin(LeadAdminBase):
    """Emergency callbacks — newest first, phone number front and centre."""

    list_display = ("created_at", "phone", "postcode", "issue", "status", "called_back_at")
    list_editable = ("status",)
    search_fields = ("phone", "postcode", "details", "name")
    autocomplete_fields = ("issue",)
    csv_fields = [
        "created_at",
        "phone",
        "name",
        "postcode",
        "issue",
        "details",
        "status",
        "called_back_at",
        "source_url",
    ]
    fieldsets = (
        ("The call", {"fields": ("phone", "name", "postcode", "issue", "details")}),
        ("Pipeline", {"fields": ("status", "called_back_at")}),
        (
            "Where it came from",
            {"classes": ("collapse",), "fields": ("source_url", "referrer", "user_agent")},
        ),
        (
            "Timestamps",
            {"classes": ("collapse",), "fields": ("created_at", "updated_at", "notified_at")},
        ),
    )


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(LeadAdminBase):
    """Contact-page enquiries."""

    list_display = ("created_at", "name", "company", "enquiry_type", "phone", "email", "status")
    list_editable = ("status",)
    list_filter = ("status", "enquiry_type", "created_at")
    search_fields = ("name", "company", "phone", "email", "message")
    autocomplete_fields = ("enquiry_type",)
    csv_fields = [
        "created_at",
        "name",
        "company",
        "phone",
        "email",
        "enquiry_type",
        "message",
        "status",
        "source_url",
    ]
    fieldsets = (
        ("Who", {"fields": ("name", "company", "phone", "email", "consent")}),
        ("What", {"fields": ("enquiry_type", "message")}),
        ("Pipeline", {"fields": ("status",)}),
        (
            "Where it came from",
            {"classes": ("collapse",), "fields": ("source_url", "referrer", "user_agent")},
        ),
        (
            "Timestamps",
            {"classes": ("collapse",), "fields": ("created_at", "updated_at", "notified_at")},
        ),
    )


@admin.register(FormFieldChoice)
class FormFieldChoiceAdmin(admin.ModelAdmin):
    """Dropdown options for every form, grouped by field."""

    list_display = ("label", "group", "value", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("label", "value")
    prepopulated_fields = {"value": ("label",)}
    ordering = ("group", "order")
