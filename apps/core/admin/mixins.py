"""Reusable admin building blocks: thumbnails, SEO fieldsets, ordering helpers."""

from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html

SEO_FIELDSET = (
    "Search engine settings",
    {
        "classes": ("collapse",),
        "fields": ("meta_title", "meta_description", "canonical_url", "og_image", "noindex"),
        "description": "Optional. Control how this page appears in Google and when shared. "
        "Leave blank to use sensible defaults.",
    },
)

PUBLISHING_FIELDSET = (
    "Publishing",
    {
        "fields": ("status", "published_at"),
        "description": "Only 'Published' items appear on the website.",
    },
)


def thumbnail_html(field: FieldFile | None, height: int = 40) -> str:
    """Render a small preview for an image/file field.

    Args:
        field: The file field (may be empty).
        height: Preview height in pixels.

    Returns:
        HTML ``<img>`` or an em dash.
    """
    if not field:
        return "—"
    return format_html(
        '<img src="{}" alt="" style="height:{}px;max-width:160px;object-fit:contain;'
        'background:#f4f7fb;border-radius:6px;padding:4px">',
        field.url,
        height,
    )


class ThumbnailMixin:
    """Adds ``thumbnail`` (list) and ``image_preview`` (form) columns.

    Set ``thumbnail_field`` to the name of the image field.
    """

    thumbnail_field = "image"

    @admin.display(description="Preview")
    def thumbnail(self, obj: Any) -> str:
        """Small preview for list views."""
        return thumbnail_html(getattr(obj, self.thumbnail_field, None))

    @admin.display(description="Current image")
    def image_preview(self, obj: Any) -> str:
        """Larger preview for the change form."""
        return thumbnail_html(getattr(obj, self.thumbnail_field, None), height=120)


class OrderedActiveAdminMixin:
    """Sensible defaults for models with ``order`` and ``is_active``."""

    ordering = ("order", "pk")
    save_on_top = False
    list_per_page = 50


class LogoAdminBase(ThumbnailMixin, OrderedActiveAdminMixin, admin.ModelAdmin):
    """Shared admin for TrustBadge, BrandServiced and ClientLogo."""

    thumbnail_field = "logo"
    list_display = ("thumbnail", "name", "order", "is_active")
    list_display_links = ("name",)
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("logo_preview",)
    fields = ("name", "logo", "logo_preview", "alt_text", "website_url", "order", "is_active")

    @admin.display(description="Current logo")
    def logo_preview(self, obj: Any) -> str:
        """Preview of the uploaded logo on the change form."""
        return thumbnail_html(obj.logo, height=80)


class PublishableAdminMixin:
    """List defaults for models inheriting ``PublishableModel``."""

    list_filter = ("status",)
    date_hierarchy = "published_at"
    readonly_fields = ("created_at", "updated_at")
    actions = ("make_published", "make_draft")

    @admin.action(description="Publish selected items")
    def make_published(self, request: Any, queryset: Any) -> None:
        """Bulk publish."""
        from apps.core.models import PublishStatus

        queryset.update(status=PublishStatus.PUBLISHED)

    @admin.action(description="Unpublish (set to draft)")
    def make_draft(self, request: Any, queryset: Any) -> None:
        """Bulk unpublish."""
        from apps.core.models import PublishStatus

        queryset.update(status=PublishStatus.DRAFT)
