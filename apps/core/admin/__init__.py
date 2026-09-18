"""Admin registrations for the core app and site-wide admin branding."""

from django.contrib import admin

from apps.core.models import (
    BrandServiced,
    ClientLogo,
    IntentCard,
    NavigationItem,
    SiteSettings,
    TrustBadge,
)

from .mixins import LogoAdminBase, OrderedActiveAdminMixin, ThumbnailMixin
from .settings import SiteSettingsAdmin

admin.site.site_header = "Mehr Cool — Website admin"
admin.site.site_title = "Mehr Cool admin"
admin.site.index_title = "Manage your website"
admin.site.empty_value_display = "—"

admin.site.register(SiteSettings, SiteSettingsAdmin)


@admin.register(NavigationItem)
class NavigationItemAdmin(OrderedActiveAdminMixin, admin.ModelAdmin):
    """Header and footer menus."""

    list_display = (
        "label",
        "subtitle",
        "parent",
        "target_type",
        "resolved_link",
        "show_in_header",
        "show_in_footer",
        "order",
        "is_active",
    )
    list_editable = ("show_in_header", "show_in_footer", "order", "is_active")
    list_filter = ("show_in_header", "show_in_footer", "is_active", "target_type")
    search_fields = ("label", "url")
    autocomplete_fields = ("parent", "service_category", "service", "page", "location")
    fieldsets = (
        (
            None,
            {
                "fields": ("label", "subtitle", "icon", "parent", "order", "is_active"),
                "description": "The caption and icon are optional — the menu looks "
                "right without them.",
            },
        ),
        (
            "Where it goes",
            {
                "fields": ("target_type", "url", "service_category", "service", "page", "location"),
                "description": "Pick what the item links to, then fill in only the matching field.",
            },
        ),
        ("Where it shows", {"fields": ("show_in_header", "show_in_footer", "open_in_new_tab")}),
    )

    @admin.display(description="Link")
    def resolved_link(self, obj: NavigationItem) -> str:
        """Show the resolved URL in the list."""
        return obj.get_url() or "—"


@admin.register(TrustBadge)
class TrustBadgeAdmin(LogoAdminBase):
    """Accreditations — off by default until the certificate is confirmed."""

    list_display = (
        "thumbnail",
        "name",
        "certificate_number",
        "show_in_header",
        "order",
        "is_active",
    )
    list_editable = ("show_in_header", "order", "is_active")
    fields = None
    fieldsets = (
        (None, {"fields": ("name", "logo", "logo_preview", "alt_text", "is_active", "order")}),
        (
            "Certificate",
            {
                "fields": (
                    "short_description",
                    "certificate_number",
                    "certificate_url",
                    "website_url",
                ),
            },
        ),
        (
            "Header",
            {
                "fields": ("show_in_header",),
                "description": "Only one badge should be ticked here — normally F-Gas.",
            },
        ),
    )


@admin.register(BrandServiced)
class BrandServicedAdmin(LogoAdminBase):
    """Manufacturer logos."""


@admin.register(ClientLogo)
class ClientLogoAdmin(LogoAdminBase):
    """Client logos."""


@admin.register(IntentCard)
class IntentCardAdmin(OrderedActiveAdminMixin, admin.ModelAdmin):
    """The three 'I need…' tiles."""

    list_display = ("label", "description", "url", "is_emergency", "order", "is_active")
    list_editable = ("order", "is_active")
    fields = ("label", "description", "icon", "url", "is_emergency", "order", "is_active")


__all__ = ["ThumbnailMixin"]
