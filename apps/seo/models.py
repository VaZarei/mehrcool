"""Abstract SEO fields mixed into every public content model."""

from __future__ import annotations

from django.db import models

from apps.core.constants import RECOMMENDED_OG_IMAGE_SIZE
from apps.core.validators import validate_image_upload_size

META_TITLE_MAX = 70
META_DESCRIPTION_MAX = 160


class SEOFieldsModel(models.Model):
    """Per-page search-engine overrides.

    Every field is optional; templates fall back to the object's own title/summary and
    then to the site-wide defaults in ``SiteSettings``.
    """

    meta_title = models.CharField(
        max_length=META_TITLE_MAX,
        blank=True,
        verbose_name="Search result title",
        help_text="Title shown in Google. Leave blank to use the page title. "
        f"Max {META_TITLE_MAX} characters; 50–60 is ideal.",
    )
    meta_description = models.CharField(
        max_length=META_DESCRIPTION_MAX,
        blank=True,
        verbose_name="Search result description",
        help_text="Two sentences shown under the title in Google. "
        f"Max {META_DESCRIPTION_MAX} characters.",
    )
    canonical_url = models.URLField(
        blank=True,
        verbose_name="Canonical URL override",
        help_text="Advanced. Only fill in if this page duplicates another page that should "
        "rank instead.",
    )
    og_image = models.ImageField(
        upload_to="og/",
        blank=True,
        validators=[validate_image_upload_size],
        verbose_name="Social sharing image",
        help_text="Shown when this page is shared on LinkedIn/WhatsApp. Leave blank to use the "
        "page's main image or the site default. " + RECOMMENDED_OG_IMAGE_SIZE,
    )
    noindex = models.BooleanField(
        default=False,
        verbose_name="Hide from search engines",
        help_text="Tick to ask Google not to list this page. Use for thank-you pages only.",
    )

    class Meta:
        abstract = True

    def get_seo_title(self) -> str:
        """Title for the ``<title>`` tag before the site suffix is applied.

        Returns:
            The meta title override or a title-like attribute of the object.
        """
        return self.meta_title or getattr(self, "title", None) or getattr(self, "name", "")

    def get_seo_description(self) -> str:
        """Description for ``<meta name="description">``.

        Returns:
            The override, or the first summary-like attribute found, or ``''``.
        """
        if self.meta_description:
            return self.meta_description
        for attr in ("short_summary", "intro", "summary", "description"):
            value = getattr(self, attr, "")
            if value:
                return str(value)[:META_DESCRIPTION_MAX]
        return ""

    def get_og_image_field(self) -> models.fields.files.FieldFile | None:
        """Best image for social sharing.

        Returns:
            The explicit OG image, else a ``hero_image``/``image`` field, else ``None``.
        """
        for attr in ("og_image", "hero_image", "image"):
            value = getattr(self, attr, None)
            if value:
                return value
        return None
