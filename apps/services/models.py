"""Service categories, services, their specifications and FAQs."""

from __future__ import annotations

from django.db import models
from django.urls import reverse

from apps.core.constants import ICON_CHOICES, RECOMMENDED_CARD_IMAGE_SIZE
from apps.core.models import OrderableModel, PublishableModel, PublishedQuerySet, TimeStampedModel
from apps.core.validators import validate_image_upload_size
from apps.pages.models import ContentBlockBase
from apps.seo.models import SEOFieldsModel


class ServiceCategoryQuerySet(PublishedQuerySet):
    """Adds prefetching helpers for category listings."""

    def with_published_services(self) -> ServiceCategoryQuerySet:
        """Prefetch published services onto ``published_services``.

        Returns:
            Queryset with a ``published_services`` attribute on each category.
        """
        return self.prefetch_related(
            models.Prefetch(
                "services",
                queryset=Service.objects.published().order_by("order", "name"),
                to_attr="published_services",
            )
        )


class ServiceCategory(PublishableModel, OrderableModel, SEOFieldsModel):
    """A hub grouping related services: Air Conditioning, Commercial Refrigeration, Emergency."""

    name = models.CharField(max_length=80, help_text="e.g. Commercial Refrigeration")
    slug = models.SlugField(
        max_length=80,
        unique=True,
        help_text="Web address, e.g. 'commercial-refrigeration' becomes "
        "/commercial-refrigeration/. Changing this breaks existing links.",
    )
    headline = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional larger heading on the hub page. Defaults to the name.",
    )
    intro = models.TextField(
        max_length=900,
        help_text="Two or three sentences at the top of the hub page.",
    )
    hero_image = models.ImageField(
        upload_to="services/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    hero_image_alt = models.CharField(max_length=160, blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="snowflake")
    audience = models.CharField(
        max_length=120,
        blank=True,
        default="Contract buyers comparing suppliers; emergency callers land on the "
        "emergency page instead.",
        help_text="Internal note: who is this hub for?",
    )

    objects = ServiceCategoryQuerySet.as_manager()

    class Meta(OrderableModel.Meta):
        verbose_name = "Service category"
        verbose_name_plural = "Service categories"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Public URL for the hub.

        Returns:
            ``/<slug>/``.
        """
        return reverse("services:category", kwargs={"category_slug": self.slug})

    @property
    def display_headline(self) -> str:
        """Heading to render on the hub page.

        Returns:
            ``headline`` or ``name``.
        """
        return self.headline or self.name


class ServiceQuerySet(PublishedQuerySet):
    """Common prefetches for service pages and cards."""

    def for_cards(self) -> ServiceQuerySet:
        """Prefetch what service cards need.

        Returns:
            Queryset with category joined.
        """
        return self.select_related("category")

    def for_detail(self) -> ServiceQuerySet:
        """Prefetch everything the detail page renders.

        Returns:
            Queryset with related rows loaded in a fixed number of queries.
        """
        from apps.core.models import BrandServiced

        return self.select_related("category").prefetch_related(
            "specifications",
            "faqs",
            "blocks__gallery_images",
            models.Prefetch(
                "brands",
                queryset=BrandServiced.objects.filter(is_active=True),
                to_attr="brand_list",
            ),
            models.Prefetch(
                "related_services",
                queryset=Service.objects.published().select_related("category"),
                to_attr="related_list",
            ),
        )


class Service(PublishableModel, OrderableModel, SEOFieldsModel):
    """An individual service such as 'Walk-In Cold Rooms' or 'VRF/VRV Installation'."""

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services",
        help_text="Which hub this service is listed under.",
    )
    name = models.CharField(max_length=100, help_text="e.g. Walk-In Cold Rooms")
    slug = models.SlugField(
        max_length=100,
        help_text="Web address within the category, e.g. 'walk-in-cold-rooms' becomes "
        "/commercial-refrigeration/walk-in-cold-rooms/.",
    )
    short_summary = models.CharField(
        max_length=200,
        help_text="One sentence shown on cards and in Google. Max 200 characters.",
    )
    intro = models.TextField(
        max_length=800,
        blank=True,
        help_text="Opening paragraph on the service page.",
    )
    hero_image = models.ImageField(
        upload_to="services/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    hero_image_alt = models.CharField(max_length=160, blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="snowflake")
    typical_response_time = models.CharField(
        max_length=60,
        blank=True,
        help_text="e.g. 'Same day' or 'Within 2 hours, 24/7'. Shown as a fact chip.",
    )
    price_from_note = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. 'PPM contracts from £45 per unit per visit'. Leave blank to hide.",
    )
    brands = models.ManyToManyField(
        "core.BrandServiced",
        blank=True,
        related_name="services",
        help_text="Manufacturers you install or maintain for this service.",
    )
    related_services = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        help_text="Shown as 'You may also need' at the bottom of the page.",
    )
    related_case_studies = models.ManyToManyField(
        "projects.CaseStudy",
        blank=True,
        related_name="featured_on_services",
        help_text="Proof: pick up to three relevant case studies.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Show this service in the homepage 'What we do' grid.",
    )
    is_emergency = models.BooleanField(
        default=False,
        help_text="Tick for emergency services so cards use the orange call button.",
    )

    objects = ServiceQuerySet.as_manager()

    class Meta(OrderableModel.Meta):
        verbose_name = "Service"
        verbose_name_plural = "Services"
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"], name="unique_service_slug_per_category"
            )
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Public URL for the service.

        Returns:
            ``/<category-slug>/<slug>/``.
        """
        return reverse(
            "services:detail",
            kwargs={"category_slug": self.category.slug, "slug": self.slug},
        )


class ServiceSpecification(OrderableModel):
    """A label/value technical specification row on a service page."""

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="specifications")
    label = models.CharField(max_length=60, help_text="e.g. Refrigerants")
    value = models.CharField(max_length=160, help_text="e.g. R290, R32, R448A, R449A")

    class Meta(OrderableModel.Meta):
        verbose_name = "Technical specification"
        verbose_name_plural = "Technical specifications"

    def __str__(self) -> str:
        return f"{self.label}: {self.value}"


class ServiceFAQ(OrderableModel, TimeStampedModel):
    """A question and answer shown in the accordion and emitted as FAQPage schema."""

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=200)
    answer = models.TextField(help_text="Plain text. Google shows this directly in search results.")

    class Meta(OrderableModel.Meta):
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self) -> str:
        return self.question


class ServiceBlock(ContentBlockBase):
    """A content block that belongs to a ``Service`` (the block-based long description)."""

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="blocks")

    class Meta(ContentBlockBase.Meta):
        verbose_name = "Content block"
        verbose_name_plural = "Content blocks"
