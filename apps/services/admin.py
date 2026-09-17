"""Admin for service categories and services."""

from __future__ import annotations

from django.contrib import admin

from apps.core.admin.mixins import (
    PUBLISHING_FIELDSET,
    SEO_FIELDSET,
    PublishableAdminMixin,
    ThumbnailMixin,
)
from apps.pages.admin import BlockInlineBase

from .models import Service, ServiceBlock, ServiceCategory, ServiceFAQ, ServiceSpecification


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(PublishableAdminMixin, ThumbnailMixin, admin.ModelAdmin):
    """The three hubs."""

    thumbnail_field = "hero_image"
    list_display = ("thumbnail", "name", "slug", "service_count", "status", "order")
    list_display_links = ("name",)
    list_editable = ("status", "order")
    search_fields = ("name", "intro")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "headline", "intro", "icon", "order", "audience")}),
        ("Hero image", {"fields": ("hero_image", "image_preview", "hero_image_alt")}),
        PUBLISHING_FIELDSET,
        SEO_FIELDSET,
    )
    readonly_fields = ("image_preview", "created_at", "updated_at")

    @admin.display(description="Services")
    def service_count(self, obj: ServiceCategory) -> int:
        """Number of services in the hub."""
        return obj.services.count()


class SpecificationInline(admin.TabularInline):
    """Label/value rows."""

    model = ServiceSpecification
    extra = 1
    fields = ("label", "value", "order")


class FAQInline(admin.StackedInline):
    """Question/answer rows."""

    model = ServiceFAQ
    extra = 0
    fields = ("question", "answer", "order")
    classes = ("collapse",)


class ServiceBlockInline(BlockInlineBase):
    """Long-description blocks."""

    model = ServiceBlock


@admin.register(Service)
class ServiceAdmin(PublishableAdminMixin, ThumbnailMixin, admin.ModelAdmin):
    """Individual services."""

    thumbnail_field = "hero_image"
    list_display = (
        "thumbnail",
        "name",
        "category",
        "is_featured",
        "is_emergency",
        "status",
        "order",
    )
    list_display_links = ("name",)
    list_editable = ("is_featured", "status", "order")
    list_filter = ("status", "category", "is_featured", "is_emergency")
    search_fields = ("name", "short_summary", "intro")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "related_services", "related_case_studies")
    filter_horizontal = ("brands",)
    inlines = (SpecificationInline, FAQInline, ServiceBlockInline)
    save_on_top = True
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "short_summary",
                    "intro",
                    "icon",
                    "order",
                )
            },
        ),
        ("Hero image", {"fields": ("hero_image", "image_preview", "hero_image_alt")}),
        (
            "Facts & proof",
            {
                "fields": (
                    "typical_response_time",
                    "price_from_note",
                    "brands",
                    "related_services",
                    "related_case_studies",
                )
            },
        ),
        ("Homepage & styling", {"fields": ("is_featured", "is_emergency")}),
        PUBLISHING_FIELDSET,
        SEO_FIELDSET,
        ("Timestamps", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):  # type: ignore[no-untyped-def]
        """Join the category for the list view."""
        return super().get_queryset(request).select_related("category")
