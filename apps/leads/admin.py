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

    list_display = ("created_at", "name", "company", "enquiry_type", "equipment_type", "phone", "email", "status")
    list_editable = ("status",)
    list_filter = ("status", "enquiry_type", "equipment_type", "created_at")
    search_fields = ("name", "company", "phone", "email", "message")
    autocomplete_fields = ("enquiry_type", "equipment_type")
    csv_fields = [
        "created_at",
        "name",
        "company",
        "phone",
        "email",
        "enquiry_type",
        "equipment_type",
        "message",
        "status",
        "source_url",
    ]
    fieldsets = (
        ("Who", {"fields": ("name", "company", "phone", "email", "consent")}),
        ("What", {"fields": ("enquiry_type", "equipment_type", "message")}),
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


from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import RepairRequest


@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    # ------------------------------------------------------------------
    # 1. LIST VIEW CONFIGURATION
    # ------------------------------------------------------------------
    list_display = (
        'ticket_number_badge',
        'full_name',
        'urgency_badge',
        'property_type',
        'equipment_type',
        'status_badge',
        'preferred_schedule',
        'created_at',
    )
    
    list_display_links = ('ticket_number_badge', 'full_name')
    
    list_filter = (
        'status',
        'urgency',
        'property_type',
        'equipment_type',
        'created_at',
    )
    
    search_fields = (
        'ticket_number',
        'full_name',
        'phone_number',
        'email',
        'service_address',
    )
    
    ordering = ('-created_at',)
    
    readonly_fields = ('ticket_number', 'created_at', 'photo_preview', 'formatted_symptoms')

    # ------------------------------------------------------------------
    # 2. DETAIL FORM LAYOUT
    # ------------------------------------------------------------------
    fieldsets = (
        ('Ticket Overview', {
            'fields': (
                ('ticket_number', 'status'),
                ('urgency', 'property_type'),
                'created_at',
            ),
            'classes': ('wide',),
        }),
        ('Customer & Contact Details', {
            'fields': (
                ('full_name', 'phone_number'),
                'email',
                'service_address',
                'access_notes',
            ),
        }),
        ('Equipment & Diagnostics', {
            'fields': (
                ('equipment_type', 'brand_model'),
                'formatted_symptoms',
                'equipment_photo',
                'photo_preview',
            ),
        }),
        ('Scheduling Details', {
            'description': 'Applicable primarily for non-emergency requests.',
            'fields': (
                ('preferred_date', 'preferred_time_slot'),
            ),
        }),
    )

    # ------------------------------------------------------------------
    # 3. CUSTOM DISPLAY METHODS
    # ------------------------------------------------------------------
    @admin.display(description='Ticket #', ordering='ticket_number')
    def ticket_number_badge(self, obj):
        return format_html(
            '<strong style="font-family: monospace; font-size: 1.1em;">{}</strong>',
            obj.ticket_number
        )

    @admin.display(description='Urgency', ordering='urgency')
    def urgency_badge(self, obj):
        if obj.urgency == 'EMERGENCY':
            return mark_safe(
                '<span style="background-color: #ff4d4f; color: white; padding: 3px 8px; '
                'border-radius: 4px; font-weight: bold;">⚡ Emergency</span>'
            )
        return mark_safe(
            '<span style="background-color: #52c41a; color: white; padding: 3px 8px; '
            'border-radius: 4px;">📅 Scheduled</span>'
        )

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        colors = {
            'PENDING': '#faad14',      # Orange
            'IN_PROGRESS': '#1890ff',  # Blue
            'COMPLETED': '#52c41a',    # Green
            'CANCELLED': '#bfbfbf',    # Grey
        }
        bg_color = colors.get(obj.status, '#d9d9d9')
        status_text = getattr(obj, 'get_status_display', lambda: obj.status)()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-weight: 500;">{}</span>',
            bg_color,
            status_text
        )

    @admin.display(description='Preferred Schedule')
    def preferred_schedule(self, obj):
        if obj.preferred_date:
            time_slot = f" ({obj.preferred_time_slot})" if obj.preferred_time_slot else ""
            return f"{obj.preferred_date}{time_slot}"
        return "-"

    @admin.display(description='Symptoms Overview')
    def formatted_symptoms(self, obj):
        if not obj.symptoms:
            return "No symptoms recorded."
        
        if isinstance(obj.symptoms, list):
            escaped_items = "".join([f"<li>{format_html('{}', item)}</li>" for item in obj.symptoms])
            return mark_safe(f'<ul style="margin: 0; padding-left: 20px;">{escaped_items}</ul>')
        
        return str(obj.symptoms)

    @admin.display(description='Photo Preview')
    def photo_preview(self, obj):
        if obj.equipment_photo:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 150px; max-width: 250px; border-radius: 6px; border: 1px solid #ccc;" />'
                '</a>',
                obj.equipment_photo.url,
                obj.equipment_photo.url
            )
        return "No photo uploaded."