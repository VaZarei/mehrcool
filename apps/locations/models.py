"""Service areas: one landing page per borough or town."""

from __future__ import annotations

from django.db import models
from django.urls import reverse

from apps.core.constants import RECOMMENDED_CARD_IMAGE_SIZE
from apps.core.models import OrderableModel, PublishableModel
from apps.core.validators import validate_image_upload_size
from apps.seo.models import SEOFieldsModel


class AreaRegion(models.TextChoices):
    """Grouping used on the areas index."""

    CENTRAL_LONDON = "central", "Central London"
    EAST_LONDON = "east", "East London"
    NORTH_LONDON = "north", "North London"
    SOUTH_LONDON = "south", "South London"
    WEST_LONDON = "west", "West London"
    GREATER_LONDON = "greater", "Greater London"
    BERKSHIRE = "berkshire", "Berkshire"
    OTHER = "other", "Other"


class ServiceArea(PublishableModel, OrderableModel, SEOFieldsModel):
    """A borough or town with its own landing page.

    Case studies and testimonials tagged with this area appear automatically.
    """

    name = models.CharField(max_length=80, help_text="e.g. Canary Wharf, Westminster, Reading")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Web address, e.g. 'canary-wharf' becomes "
        "/areas/air-conditioning-refrigeration-canary-wharf/.",
    )
    region = models.CharField(
        max_length=12,
        choices=AreaRegion.choices,
        default=AreaRegion.CENTRAL_LONDON,
        help_text="Groups the area on the 'Areas we cover' page.",
    )
    custom_h1 = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Custom page heading",
        help_text="Leave blank for 'Commercial refrigeration & air conditioning in <Name>'.",
    )
    intro = models.TextField(
        max_length=1200,
        help_text="Two or three paragraphs specific to this area: typical clients, local "
        "landmarks, travel time from base.",
    )
    postcode_prefixes = models.CharField(
        max_length=120,
        blank=True,
        help_text="Comma-separated, e.g. E14, E1W. Shown as 'Covering E14, E1W'.",
    )
    typical_response_time = models.CharField(
        max_length=60,
        blank=True,
        help_text="e.g. 'Under 60 minutes'. Leave blank to use the site-wide promise.",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    hero_image = models.ImageField(
        upload_to="areas/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    hero_image_alt = models.CharField(max_length=160, blank=True)

    class Meta(OrderableModel.Meta):
        ordering = ["region", "order", "name"]
        verbose_name = "Service area"
        verbose_name_plural = "Service areas"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Public URL for the area landing page.

        Returns:
            ``/areas/air-conditioning-refrigeration-<slug>/``.
        """
        return reverse("locations:detail", kwargs={"slug": self.slug})

    @property
    def display_h1(self) -> str:
        """Page heading with fallback.

        Returns:
            ``custom_h1`` or the generated default.
        """
        return self.custom_h1 or f"Commercial refrigeration & air conditioning in {self.name}"

    @property
    def postcode_list(self) -> list[str]:
        """Postcode prefixes as a clean list.

        Returns:
            Stripped, non-empty prefixes.
        """
        return [p.strip() for p in self.postcode_prefixes.split(",") if p.strip()]
