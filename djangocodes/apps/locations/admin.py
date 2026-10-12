"""Admin for service areas."""

from __future__ import annotations

from django.contrib import admin

from apps.core.admin.mixins import (
    PUBLISHING_FIELDSET,
    SEO_FIELDSET,
    PublishableAdminMixin,
    ThumbnailMixin,
)

from .models import ServiceArea


@admin.register(ServiceArea)
class ServiceAreaAdmin(PublishableAdminMixin, ThumbnailMixin, admin.ModelAdmin):
    """Borough / town landing pages. Creating one takes under a minute."""

    thumbnail_field = "hero_image"
    list_display = ("name", "region", "postcode_prefixes", "status", "order")
    list_editable = ("status", "order")
    list_filter = ("status", "region")
    search_fields = ("name", "postcode_prefixes", "intro")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "slug", "region", "custom_h1", "intro"),
                "description": "Only name, slug, region and intro are required. Case studies and "
                "reviews tagged with this area appear on the page automatically.",
            },
        ),
        (
            "Local facts",
            {"fields": ("postcode_prefixes", "typical_response_time", ("latitude", "longitude"))},
        ),
        (
            "Hero image",
            {"classes": ("collapse",), "fields": ("hero_image", "image_preview", "hero_image_alt")},
        ),
        PUBLISHING_FIELDSET,
        SEO_FIELDSET,
    )
