"""Sectors served and case studies proving competence to contract buyers."""

from __future__ import annotations

from django.db import models
from django.urls import reverse

from apps.core.constants import ICON_CHOICES, RECOMMENDED_CARD_IMAGE_SIZE
from apps.core.models import OrderableModel, PublishableModel, PublishedQuerySet, TimeStampedModel
from apps.core.validators import validate_image_upload_size
from apps.seo.models import SEOFieldsModel


class Sector(PublishableModel, OrderableModel, SEOFieldsModel):
    """A market segment: Restaurants, Supermarkets, Hotels, Offices, Healthcare, Data Centres."""

    name = models.CharField(max_length=80)
    slug = models.SlugField(
        max_length=80, unique=True, help_text="e.g. 'restaurants' becomes /sectors/restaurants/."
    )
    headline = models.CharField(
        max_length=120,
        blank=True,
        help_text="Heading on the sector page. Defaults to the name.",
    )
    intro = models.TextField(
        max_length=800, help_text="Why this sector's cooling needs are different."
    )
    hero_image = models.ImageField(
        upload_to="sectors/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    hero_image_alt = models.CharField(max_length=160, blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default="building")
    key_services = models.ManyToManyField(
        "services.Service",
        blank=True,
        related_name="sectors",
        help_text="Services most relevant to this sector, shown as cards.",
    )

    class Meta(OrderableModel.Meta):
        verbose_name = "Sector"
        verbose_name_plural = "Sectors"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Public URL for the sector page.

        Returns:
            ``/sectors/<slug>/``.
        """
        return reverse("projects:sector", kwargs={"slug": self.slug})

    @property
    def display_headline(self) -> str:
        """Heading to render.

        Returns:
            ``headline`` or ``name``.
        """
        return self.headline or self.name


class CaseStudyQuerySet(PublishedQuerySet):
    """Prefetches for case study listings and detail pages."""

    def for_cards(self) -> CaseStudyQuerySet:
        """Load what a card needs in one query.

        Returns:
            Queryset with sector and area joined.
        """
        return self.select_related("sector", "area")

    def for_detail(self) -> CaseStudyQuerySet:
        """Load everything the detail page renders.

        Returns:
            Queryset with all relations prefetched.
        """
        return self.select_related("sector", "area", "testimonial").prefetch_related(
            "services__category", "images"
        )


class CaseStudy(PublishableModel, SEOFieldsModel):
    """A completed project written up as challenge → solution → result."""

    title = models.CharField(
        max_length=140, help_text="e.g. 'Walk-in freezer replacement for a Soho restaurant group'"
    )
    slug = models.SlugField(max_length=140, unique=True)
    client_name = models.CharField(
        max_length=120,
        help_text="Real client name. Tick 'Anonymise' below if you cannot name them publicly.",
    )
    client_anonymised = models.BooleanField(
        default=False,
        verbose_name="Anonymise client",
        help_text="Shows the sector instead of the client name (e.g. 'A Mayfair hotel').",
    )
    anonymised_label = models.CharField(
        max_length=120,
        blank=True,
        help_text="What to show instead of the client name, e.g. 'A Mayfair boutique hotel'.",
    )
    sector = models.ForeignKey(
        Sector, on_delete=models.PROTECT, related_name="case_studies", help_text="Client's sector."
    )
    area = models.ForeignKey(
        "locations.ServiceArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="case_studies",
        help_text="Borough or town. Lets the area landing page show this project.",
    )
    services = models.ManyToManyField(
        "services.Service",
        related_name="case_studies",
        help_text="Services delivered on this project.",
    )
    scale_metric = models.CharField(
        max_length=80,
        blank=True,
        help_text="One measurable fact, e.g. '800 sqm venue' or '14 display cabinets'.",
    )
    summary = models.CharField(
        max_length=200, help_text="One sentence for cards and Google. Max 200 characters."
    )
    challenge = models.TextField(help_text="What was wrong or needed? Plain text paragraphs.")
    solution = models.TextField(help_text="What you installed or fixed, and how.")
    result = models.TextField(
        verbose_name="Result / return on investment",
        help_text="Outcome in numbers where possible: energy saved, downtime avoided, temps held.",
    )
    hero_image = models.ImageField(
        upload_to="case-studies/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    hero_image_alt = models.CharField(max_length=160, blank=True)
    testimonial = models.ForeignKey(
        "testimonials.Testimonial",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="case_studies",
        help_text="Optional quote from this client.",
    )
    completed_on = models.DateField(null=True, blank=True, help_text="When the job finished.")
    is_featured = models.BooleanField(
        default=False, help_text="Show on the homepage 'Recent work' section."
    )

    objects = CaseStudyQuerySet.as_manager()

    class Meta:
        ordering = ["-is_featured", "-completed_on", "-published_at"]
        verbose_name = "Case study"
        verbose_name_plural = "Case studies"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Public URL for the case study.

        Returns:
            ``/case-studies/<slug>/``.
        """
        return reverse("projects:case_study", kwargs={"slug": self.slug})

    @property
    def display_client(self) -> str:
        """Client label respecting the anonymise toggle.

        Returns:
            The anonymised label, the sector-based fallback, or the real client name.
        """
        if self.client_anonymised:
            return self.anonymised_label or f"A {self.sector.name.lower()} client"
        return self.client_name


class CaseStudyImage(OrderableModel, TimeStampedModel):
    """A gallery photo on a case study."""

    case_study = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="case-studies/gallery/",
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    alt_text = models.CharField(max_length=160, help_text="Describe the photo.")
    caption = models.CharField(max_length=200, blank=True)

    class Meta(OrderableModel.Meta):
        verbose_name = "Gallery photo"
        verbose_name_plural = "Gallery photos"

    def __str__(self) -> str:
        return self.alt_text
