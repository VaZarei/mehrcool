"""Content pages and the block system used to build them.

``ContentBlockBase`` is abstract so any model (pages today, services and case studies
too) can own an ordered list of blocks that all render from the same partials.
"""

from __future__ import annotations

from django.db import models
from django.urls import reverse

from apps.core.constants import RECOMMENDED_CARD_IMAGE_SIZE
from apps.core.models import OrderableModel, PublishableModel, TimeStampedModel
from apps.core.validators import validate_image_upload_size
from apps.seo.models import SEOFieldsModel


class PageTemplate(models.TextChoices):
    """Layouts a page can use."""

    STANDARD = "standard", "Standard (hero image, full-width blocks)"
    NARROW = "narrow", "Narrow reading column (legal pages, statements)"
    LANDING = "landing", "Landing page (no side padding, CTA-heavy)"


class BlockType(models.TextChoices):
    """Kinds of content block. Each renders from ``pages/blocks/<value>.html``."""

    RICH_TEXT = "rich_text", "Text"
    IMAGE_TEXT = "image_text", "Image + text side by side"
    STAT_ROW = "stat_row", "Row of statistics"
    FAQ = "faq", "FAQ accordion"
    CTA_BAND = "cta_band", "Call-to-action band"
    LOGO_STRIP = "logo_strip", "Logo strip (accreditations, brands, clients)"
    VIDEO = "video", "Video band"
    GALLERY = "gallery", "Image gallery"
    FEATURE_GRID = "feature_grid", "Feature grid (2 or 3 columns)"


class BlockBackground(models.TextChoices):
    """Background treatments available to a block."""

    WHITE = "white", "White"
    ICE = "ice", "Ice tint (light blue-grey)"
    NAVY = "navy", "Navy (dark)"


class ImagePosition(models.TextChoices):
    """Side the image sits on in an image + text block."""

    LEFT = "left", "Image on the left"
    RIGHT = "right", "Image on the right"


class LogoSource(models.TextChoices):
    """Which logo set a logo strip block shows."""

    BADGES = "badges", "Accreditation badges"
    BRANDS = "brands", "Brands we service"
    CLIENTS = "clients", "Client logos"


class Page(PublishableModel, OrderableModel, SEOFieldsModel):
    """A general content page such as About, Privacy or F-Gas Compliance Statement."""

    title = models.CharField(max_length=120, help_text="Page heading (the H1).")
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="Part of the web address, e.g. 'about' becomes /about/. Lowercase, hyphens. "
        "Special slugs 'services', 'sectors', 'case-studies', 'areas', 'contact' and "
        "'emergency-callout' control the heading and intro of those built-in pages.",
    )
    template = models.CharField(
        max_length=20,
        choices=PageTemplate.choices,
        default=PageTemplate.STANDARD,
        help_text="Overall layout of the page.",
    )
    intro = models.TextField(
        max_length=400,
        blank=True,
        help_text="One or two sentences under the heading. Also used as the Google "
        "description if none is set.",
    )
    hero_image = models.ImageField(
        upload_to="pages/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text="Optional banner image. " + RECOMMENDED_CARD_IMAGE_SIZE,
    )
    hero_image_alt = models.CharField(max_length=160, blank=True)
    show_contact_cta = models.BooleanField(
        default=True,
        help_text="Show the standard 'Talk to an engineer' band at the bottom.",
    )
    audience_note = models.CharField(
        max_length=120,
        blank=True,
        help_text="Internal only: who is this page for? (Emergency caller / Contract buyer)",
    )

    class Meta(OrderableModel.Meta):
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Public URL for the page.

        Returns:
            ``/<slug>/``.
        """
        return reverse("pages:detail", kwargs={"slug": self.slug})


class MediaAsset(TimeStampedModel):
    """A reusable image in the media library, used by gallery blocks."""

    title = models.CharField(max_length=120, help_text="Internal name so you can find it later.")
    image = models.ImageField(
        upload_to="library/",
        validators=[validate_image_upload_size],
        help_text=RECOMMENDED_CARD_IMAGE_SIZE,
    )
    alt_text = models.CharField(
        max_length=160, help_text="Describe the image for screen readers and Google."
    )
    caption = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Media library image"
        verbose_name_plural = "Media library"

    def __str__(self) -> str:
        return self.title


class ContentBlockBase(OrderableModel, TimeStampedModel):
    """Abstract block: one section of a page, service or case study.

    Repeated items (statistics, FAQs, feature columns) are typed one per line in
    ``items`` using ``Title :: Body :: Link`` so they can be edited inline in the admin
    without nested forms.
    """

    block_type = models.CharField(
        max_length=20,
        choices=BlockType.choices,
        default=BlockType.RICH_TEXT,
        help_text="What kind of section this is. Fill in only the fields that apply.",
    )
    heading = models.CharField(
        max_length=120,
        blank=True,
        help_text="Section heading. Leave blank for none.",
    )
    body = models.TextField(
        blank=True,
        help_text="Main text. Blank line = new paragraph. Start a line with '- ' for a bullet, "
        "'## ' for a sub-heading, and wrap words in **double stars** for bold.",
    )
    items = models.TextField(
        blank=True,
        help_text="One item per line for statistics, FAQs and feature grids. Format: "
        "Title :: Body :: Link (Body and Link are optional). "
        "For FAQs use: Question? :: Answer.",
    )
    image = models.ImageField(
        upload_to="blocks/",
        blank=True,
        validators=[validate_image_upload_size],
        help_text="Used by 'Image + text'. " + RECOMMENDED_CARD_IMAGE_SIZE,
    )
    image_alt = models.CharField(max_length=160, blank=True)
    image_position = models.CharField(
        max_length=6, choices=ImagePosition.choices, default=ImagePosition.LEFT
    )
    cta_label = models.CharField(
        max_length=40, blank=True, help_text="Button text, e.g. 'Request a quote'."
    )
    cta_url = models.CharField(
        max_length=200, blank=True, help_text="Button link, e.g. /quote/ or tel:+44..."
    )
    cta_is_phone = models.BooleanField(
        default=False,
        help_text="Tick to make the button dial the emergency line instead of using the link.",
    )
    video_embed_url = models.URLField(
        blank=True,
        help_text="YouTube/Vimeo embed URL for a video band, e.g. "
        "https://www.youtube-nocookie.com/embed/VIDEO_ID",
    )
    logo_source = models.CharField(
        max_length=10,
        choices=LogoSource.choices,
        default=LogoSource.BADGES,
        help_text="Used by 'Logo strip'.",
    )
    gallery_images = models.ManyToManyField(
        MediaAsset,
        blank=True,
        help_text="Used by 'Image gallery'. Add images in the Media library first.",
    )
    columns = models.PositiveSmallIntegerField(
        default=3,
        choices=[(2, "2 columns"), (3, "3 columns"), (4, "4 columns")],
        help_text="Used by 'Feature grid' and 'Row of statistics'.",
    )
    background = models.CharField(
        max_length=6, choices=BlockBackground.choices, default=BlockBackground.WHITE
    )
    anchor_id = models.SlugField(
        max_length=40,
        blank=True,
        help_text="Optional. Lets you link straight to this section with #your-anchor.",
    )

    class Meta(OrderableModel.Meta):
        abstract = True

    def __str__(self) -> str:
        return f"{self.get_block_type_display()}: {self.heading or '(no heading)'}"

    @property
    def template_name(self) -> str:
        """Partial used to render this block.

        Returns:
            Template path such as ``'pages/blocks/faq.html'``.
        """
        return f"pages/blocks/{self.block_type}.html"

    @property
    def parsed_items(self) -> list[dict[str, str]]:
        """Parse ``items`` into dicts with ``title``, ``body`` and ``url`` keys.

        Returns:
            One dict per non-empty line.
        """
        from .services import parse_block_items

        return parse_block_items(self.items)

    @property
    def faq_entries(self) -> list[FAQEntry]:
        """FAQ-shaped view of ``parsed_items`` for the FAQPage schema builder.

        Returns:
            List of lightweight FAQ entries.
        """
        return [FAQEntry(question=i["title"], answer=i["body"]) for i in self.parsed_items]


class FAQEntry:
    """Duck-typed FAQ used by the schema builder for text-defined FAQs.

    Args:
        question: The question text.
        answer: The answer text.
    """

    def __init__(self, question: str, answer: str) -> None:
        self.question = question
        self.answer = answer


class PageBlock(ContentBlockBase):
    """A block that belongs to a ``Page``."""

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="blocks")

    class Meta(ContentBlockBase.Meta):
        verbose_name = "Content block"
        verbose_name_plural = "Content blocks"
