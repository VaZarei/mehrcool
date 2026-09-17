"""Admin-managed header and footer navigation."""

from __future__ import annotations

from django.core.cache import cache
from django.db import models

from apps.core import constants

from .base import OrderableModel, TimeStampedModel


class LinkTarget(models.TextChoices):
    """What a navigation item points at."""

    URL = "url", "A web address I type in"
    SERVICE_CATEGORY = "category", "A service category hub"
    SERVICE = "service", "An individual service"
    PAGE = "page", "A content page"
    LOCATION = "location", "An area we cover"
    NONE = "none", "No link (heading only)"


class NavigationItem(OrderableModel, TimeStampedModel):
    """A link in the header or footer, optionally nested one level under a parent."""

    label = models.CharField(
        max_length=40,
        help_text="Text shown in the menu. Keep it short — under 20 characters for the header.",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text="Leave blank for a top-level item. Pick a parent to place it in that "
        "item's dropdown (header) or column (footer).",
    )
    target_type = models.CharField(
        max_length=12,
        choices=LinkTarget.choices,
        default=LinkTarget.URL,
        verbose_name="Links to",
        help_text="Choose what this item opens, then fill in the matching field below.",
    )
    url = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Web address",
        help_text="Used when 'Links to' is a web address. Internal links like /contact/ work.",
    )
    service_category = models.ForeignKey(
        "services.ServiceCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    service = models.ForeignKey(
        "services.Service", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    page = models.ForeignKey(
        "pages.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    location = models.ForeignKey(
        "locations.ServiceArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    show_in_header = models.BooleanField(default=True, help_text="Show in the top menu.")
    show_in_footer = models.BooleanField(default=False, help_text="Show in the footer.")
    open_in_new_tab = models.BooleanField(default=False)
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide this item without deleting it."
    )

    class Meta(OrderableModel.Meta):
        verbose_name = "Navigation item"
        verbose_name_plural = "Navigation"

    def __str__(self) -> str:
        return self.label

    def save(self, *args: object, **kwargs: object) -> None:
        """Save and invalidate the cached navigation tree."""
        super().save(*args, **kwargs)
        cache.delete(constants.NAVIGATION_CACHE_KEY)

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        """Delete and invalidate the cached navigation tree."""
        result = super().delete(*args, **kwargs)
        cache.delete(constants.NAVIGATION_CACHE_KEY)
        return result

    def get_url(self) -> str:
        """Resolve the destination URL according to ``target_type``.

        Returns:
            The URL string, or ``''`` for heading-only items or unresolved targets.
        """
        target_map = {
            LinkTarget.SERVICE_CATEGORY: self.service_category,
            LinkTarget.SERVICE: self.service,
            LinkTarget.PAGE: self.page,
            LinkTarget.LOCATION: self.location,
        }
        if self.target_type == LinkTarget.URL:
            return self.url
        if self.target_type == LinkTarget.NONE:
            return ""
        obj = target_map.get(self.target_type)
        return obj.get_absolute_url() if obj is not None else ""

    @property
    def is_external(self) -> bool:
        """Whether the URL leaves the site.

        Returns:
            ``True`` for absolute http(s) URLs.
        """
        return self.get_url().startswith(("http://", "https://"))
