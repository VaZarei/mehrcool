"""Singleton admin for ``SiteSettings``: one row, edit form only, grouped fieldsets."""

from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from apps.core.constants import SITE_SETTINGS_PK
from apps.core.models import SiteSettings

from .mixins import thumbnail_html


class SiteSettingsAdmin(admin.ModelAdmin):
    """Redirects the changelist to the single edit form and blocks add/delete."""

    save_on_top = True
    readonly_fields = (
        "logo_light_preview",
        "logo_dark_preview",
        "hero_poster_preview",
        "contact_qr_preview",
        "updated_at",
    )
    fieldsets = (
        (
            "Business identity",
            {
                "fields": (
                    "trading_name",
                    "legal_name",
                    "company_number",
                    "vat_number",
                    "founded_date",
                )
            },
        ),
        (
            "Logos & favicon",
            {
                "fields": (
                    ("logo_light", "logo_light_preview"),
                    ("logo_dark", "logo_dark_preview"),
                    "favicon",
                )
            },
        ),
        (
            "Phone, WhatsApp & email",
            {
                "fields": (
                    "emergency_phone",
                    "primary_phone",
                    "whatsapp_number",
                    "whatsapp_prefill_message",
                    "email",
                    "lead_notification_email",
                ),
                "description": "The emergency phone is what every orange button dials. "
                "Change it here and it updates everywhere at once.",
            },
        ),
        (
            "Address & map",
            {
                "fields": (
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "region",
                    "postcode",
                    "country_code",
                    ("latitude", "longitude"),
                    "google_maps_embed_url",
                    "areas_served",
                )
            },
        ),
        (
            "Hours & service promise",
            {
                "fields": (
                    "opening_hours_text",
                    "is_open_24_7",
                    "response_time_claim",
                    "price_range",
                )
            },
        ),
        (
            "Emergency strip (above the header)",
            {"fields": ("emergency_banner_enabled", "emergency_banner_text")},
        ),
        (
            "Homepage hero",
            {
                "fields": (
                    "hero_headline",
                    "hero_subheadline",
                    "hero_primary_cta_label",
                    "hero_secondary_cta_label",
                    "hero_secondary_cta_url",
                    "hero_video_mp4",
                    "hero_video_webm",
                    ("hero_poster", "hero_poster_preview"),
                    "hero_poster_alt",
                    "intent_strip_heading",
                ),
                "description": "The video plays silently behind the headline on desktop. Phones "
                "show the poster image instead to save data.",
            },
        ),
        (
            "Homepage sections",
            {
                "classes": ("collapse",),
                "fields": (
                    "home_services_heading",
                    "home_services_intro",
                    "home_why_heading",
                    "home_why_items",
                    "home_proof_heading",
                    "home_reviews_heading",
                ),
            },
        ),
        (
            "Call-to-action band (bottom of most pages)",
            {
                "classes": ("collapse",),
                "fields": ("cta_band_title", "cta_band_text", "cta_band_checklist"),
            },
        ),
        (
            "Button labels & small headings",
            {
                "classes": ("collapse",),
                "fields": (
                    "mobile_bar_call_label",
                    "mobile_bar_whatsapp_label",
                    "footer_contact_heading",
                    "qr_card_title",
                ),
            },
        ),
        (
            "'Save our contact' QR code",
            {
                "fields": (("contact_qr_image", "contact_qr_preview"), "contact_qr_caption"),
                "description": "Shown on the contact page and footer. If you leave the image "
                "blank a QR code is generated automatically from the details above.",
            },
        ),
        (
            "Social & review links",
            {
                "classes": ("collapse",),
                "fields": (
                    "google_business_url",
                    "checkatrade_url",
                    "linkedin_url",
                    "facebook_url",
                    "instagram_url",
                    "x_url",
                ),
            },
        ),
        (
            "Analytics",
            {"classes": ("collapse",), "fields": ("ga4_measurement_id", "gtm_container_id")},
        ),
        (
            "Search engine defaults",
            {
                "classes": ("collapse",),
                "fields": (
                    "default_meta_title_suffix",
                    "default_meta_description",
                    "default_og_image",
                    "google_rating_override",
                    "google_review_count_override",
                ),
            },
        ),
        ("Footer", {"fields": ("footer_blurb", "footer_legal_line", "updated_at")}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Never allow a second row."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        """Never allow deletion."""
        return False

    def changelist_view(self, request: HttpRequest, extra_context: Any = None) -> HttpResponse:
        """Skip the list and open the edit form directly."""
        SiteSettings.load()
        url = reverse("admin:core_sitesettings_change", args=[SITE_SETTINGS_PK])
        return HttpResponseRedirect(url)

    @admin.display(description="Preview")
    def logo_light_preview(self, obj: SiteSettings) -> str:
        """Thumbnail of the light logo."""
        return thumbnail_html(obj.logo_light, 60)

    @admin.display(description="Preview")
    def logo_dark_preview(self, obj: SiteSettings) -> str:
        """Thumbnail of the dark logo."""
        return thumbnail_html(obj.logo_dark, 60)

    @admin.display(description="Preview")
    def hero_poster_preview(self, obj: SiteSettings) -> str:
        """Thumbnail of the hero poster."""
        return thumbnail_html(obj.hero_poster, 90)

    @admin.display(description="Preview")
    def contact_qr_preview(self, obj: SiteSettings) -> str:
        """Thumbnail of the QR code."""
        return thumbnail_html(obj.contact_qr_image, 120)
