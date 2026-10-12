"""Admin for sectors and case studies."""

from __future__ import annotations

from django.contrib import admin

from apps.core.admin.mixins import (
    PUBLISHING_FIELDSET,
    SEO_FIELDSET,
    PublishableAdminMixin,
    ThumbnailMixin,
)

from .models import CaseStudy, CaseStudyImage, Sector


@admin.register(Sector)
class SectorAdmin(PublishableAdminMixin, ThumbnailMixin, admin.ModelAdmin):
    """Markets served."""

    thumbnail_field = "hero_image"
    list_display = ("thumbnail", "name", "slug", "status", "order")
    list_display_links = ("name",)
    list_editable = ("status", "order")
    search_fields = ("name", "intro")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("key_services",)
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "headline", "intro", "icon", "order", "key_services")}),
        ("Hero image", {"fields": ("hero_image", "image_preview", "hero_image_alt")}),
        PUBLISHING_FIELDSET,
        SEO_FIELDSET,
    )


class CaseStudyImageInline(admin.TabularInline):
    """Gallery photos."""

    model = CaseStudyImage
    extra = 0
    fields = ("image", "alt_text", "caption", "order")


@admin.register(CaseStudy)
class CaseStudyAdmin(PublishableAdminMixin, ThumbnailMixin, admin.ModelAdmin):
    """Case studies."""

    thumbnail_field = "hero_image"
    list_display = (
        "thumbnail",
        "title",
        "display_client",
        "sector",
        "area",
        "is_featured",
        "status",
    )
    list_display_links = ("title",)
    list_editable = ("is_featured", "status")
    list_filter = ("status", "sector", "area", "is_featured")
    search_fields = ("title", "client_name", "summary", "challenge", "solution", "result")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("sector", "area", "services", "testimonial")
    inlines = (CaseStudyImageInline,)
    save_on_top = True
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "sector", "area", "services")}),
        (
            "Client",
            {
                "fields": ("client_name", "client_anonymised", "anonymised_label"),
                "description": "If you cannot name the client, tick 'Anonymise' and give a "
                "descriptive label instead.",
            },
        ),
        (
            "The story",
            {"fields": ("scale_metric", "challenge", "solution", "result", "completed_on")},
        ),
        ("Hero image", {"fields": ("hero_image", "image_preview", "hero_image_alt")}),
        ("Proof & placement", {"fields": ("testimonial", "is_featured")}),
        PUBLISHING_FIELDSET,
        SEO_FIELDSET,
        ("Timestamps", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):  # type: ignore[no-untyped-def]
        """Join relations shown in the list."""
        return super().get_queryset(request).select_related("sector", "area")
