"""Abstract base models shared by every content app.

Keeping these here means a future blog or client-portal app inherits timestamps,
publishing workflow and ordering behaviour without touching existing code.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Adds ``created_at`` / ``updated_at`` bookkeeping to any model."""

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class PublishStatus(models.TextChoices):
    """Publishing workflow states for public content."""

    DRAFT = "draft", "Draft (hidden from visitors)"
    PUBLISHED = "published", "Published (live on the website)"


class PublishedQuerySet(models.QuerySet):
    """QuerySet with a ``published()`` filter used by every public listing."""

    def published(self) -> PublishedQuerySet:
        """Return only rows that are live and whose publish date has passed.

        Returns:
            Filtered queryset.
        """
        return self.filter(
            status=PublishStatus.PUBLISHED,
            published_at__lte=timezone.now(),
        )


class PublishableModel(TimeStampedModel):
    """Adds a draft/published workflow with a scheduled publish date."""

    status = models.CharField(
        max_length=12,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        help_text="Only 'Published' items appear on the website. Use 'Draft' while you work.",
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="Set a future date and time to schedule publication.",
    )

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def is_published(self) -> bool:
        """Whether this object is currently visible to the public.

        Returns:
            ``True`` when status is published and the publish date has passed.
        """
        return self.status == PublishStatus.PUBLISHED and self.published_at <= timezone.now()


class OrderableModel(models.Model):
    """Adds an integer ``order`` used for admin-controlled display ordering."""

    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Lower numbers appear first. Edit these directly in the list view to reorder.",
    )

    class Meta:
        abstract = True
        ordering = ["order", "pk"]
