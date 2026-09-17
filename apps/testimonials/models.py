"""Customer testimonials with a provider abstraction ready for a live Google feed."""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import OrderableModel, PublishableModel, PublishedQuerySet


class ReviewSource(models.TextChoices):
    """Where the review was originally left."""

    GOOGLE = "google", "Google"
    TRUSTPILOT = "trustpilot", "Trustpilot"
    CHECKATRADE = "checkatrade", "Checkatrade"
    DIRECT = "direct", "Given directly to us"


class TestimonialQuerySet(PublishedQuerySet):
    """Aggregation helpers for the reviews widget and structured data."""

    def aggregate_rating(self) -> tuple[Decimal | None, int]:
        """Average rating and count over published reviews.

        Returns:
            ``(average, count)``; average is ``None`` when there are no reviews.
        """
        data = self.published().aggregate(avg=models.Avg("rating"), count=models.Count("id"))
        avg = data["avg"]
        return (Decimal(avg).quantize(Decimal("0.1")) if avg is not None else None, data["count"])

    def featured(self) -> TestimonialQuerySet:
        """Published reviews flagged for the homepage.

        Returns:
            Filtered queryset.
        """
        return self.published().filter(is_featured=True)


class Testimonial(PublishableModel, OrderableModel):
    """A single customer review."""

    author_name = models.CharField(max_length=80, help_text="e.g. 'Daniel R.' or full name.")
    author_role = models.CharField(max_length=80, blank=True, help_text="e.g. Operations Manager")
    company = models.CharField(max_length=120, blank=True, help_text="e.g. 'Bar group, Soho'")
    quote = models.TextField(max_length=600, help_text="The review text, verbatim.")
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Stars out of 5.",
    )
    source = models.CharField(
        max_length=12,
        choices=ReviewSource.choices,
        default=ReviewSource.GOOGLE,
        help_text="Where the review was left. Shown as a small label.",
    )
    source_url = models.URLField(blank=True, help_text="Link to the original review, if any.")
    date = models.DateField(help_text="When the review was left.")
    is_featured = models.BooleanField(default=False, help_text="Show on the homepage.")
    area = models.ForeignKey(
        "locations.ServiceArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="testimonials",
        help_text="Optional. Lets the area landing page show this review.",
    )
    service = models.ForeignKey(
        "services.Service",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="testimonials",
        help_text="Optional. Lets the service page show this review.",
    )

    objects = TestimonialQuerySet.as_manager()

    class Meta(OrderableModel.Meta):
        ordering = ["order", "-date"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self) -> str:
        return f"{self.author_name} — {self.rating}★"

    @property
    def attribution(self) -> str:
        """Role and company joined for display.

        Returns:
            ``'Operations Manager, Bar group'`` style string.
        """
        return ", ".join(p for p in (self.author_role, self.company) if p)
