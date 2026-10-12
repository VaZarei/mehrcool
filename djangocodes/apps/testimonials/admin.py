"""Admin for reviews."""

from __future__ import annotations

from django.contrib import admin

from apps.core.admin.mixins import PUBLISHING_FIELDSET, PublishableAdminMixin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(PublishableAdminMixin, admin.ModelAdmin):
    """Customer reviews."""

    list_display = (
        "author_name",
        "company",
        "rating",
        "source",
        "date",
        "is_featured",
        "status",
        "order",
    )
    list_editable = ("is_featured", "status", "order")
    list_filter = ("status", "source", "rating", "is_featured")
    search_fields = ("author_name", "company", "quote")
    autocomplete_fields = ("area", "service")
    fieldsets = (
        (None, {"fields": ("author_name", "author_role", "company", "quote", "rating")}),
        ("Source", {"fields": ("source", "source_url", "date")}),
        ("Placement", {"fields": ("is_featured", "area", "service", "order")}),
        PUBLISHING_FIELDSET,
    )
