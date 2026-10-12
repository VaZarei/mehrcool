"""Admin for pages, content blocks and the media library."""

from __future__ import annotations

from django.contrib import admin

from apps.core.admin.mixins import (
    PUBLISHING_FIELDSET,
    SEO_FIELDSET,
    PublishableAdminMixin,
    ThumbnailMixin,
)

from .models import MediaAsset, Page, PageBlock

BLOCK_FIELDSETS = (
    (None, {"fields": ("block_type", "heading", "order", "background", "anchor_id")}),
    ("Text", {"fields": ("body",)}),
    (
        "Repeated items (statistics, FAQs, feature grid)",
        {"classes": ("collapse",), "fields": ("items", "columns")},
    ),
    (
        "Image + text",
        {"classes": ("collapse",), "fields": ("image", "image_alt", "image_position")},
    ),
    (
        "Button (call-to-action)",
        {"classes": ("collapse",), "fields": ("cta_label", "cta_url", "cta_is_phone")},
    ),
    (
        "Video / logos / gallery",
        {"classes": ("collapse",), "fields": ("video_embed_url", "logo_source", "gallery_images")},
    ),
)


class BlockInlineBase(admin.StackedInline):
    """Shared inline configuration for every block model."""

    extra = 0
    fieldsets = BLOCK_FIELDSETS
    autocomplete_fields = ("gallery_images",)
    classes = ("collapse",)
    show_change_link = False


class PageBlockInline(BlockInlineBase):
    """Blocks on a page."""

    model = PageBlock


@admin.register(Page)
class PageAdmin(PublishableAdminMixin, admin.ModelAdmin):
    """Content pages built from blocks."""

    list_display = ("title", "slug", "template", "status", "order", "updated_at")
    list_editable = ("status", "order")
    list_filter = ("status", "template")
    search_fields = ("title", "slug", "intro")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PageBlockInline,)
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("title", "slug", "template", "intro", "audience_note")}),
        ("Banner image", {"classes": ("collapse",), "fields": ("hero_image", "hero_image_alt")}),
        ("Options", {"fields": ("show_contact_cta", "order")}),
        PUBLISHING_FIELDSET,
        SEO_FIELDSET,
        ("Timestamps", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )


@admin.register(MediaAsset)
class MediaAssetAdmin(ThumbnailMixin, admin.ModelAdmin):
    """Reusable images for galleries."""

    list_display = ("thumbnail", "title", "alt_text", "created_at")
    list_display_links = ("title",)
    search_fields = ("title", "alt_text", "caption")
    readonly_fields = ("image_preview",)
    fields = ("title", "image", "image_preview", "alt_text", "caption")
