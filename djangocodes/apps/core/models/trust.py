"""Trust signals (accreditations, brands, client logos) and the homepage intent tiles."""

from __future__ import annotations

from django.core.validators import FileExtensionValidator
from django.db import models

from apps.core import constants
from apps.core.validators import validate_image_upload_size

from .base import OrderableModel, TimeStampedModel


class LogoModelBase(OrderableModel, TimeStampedModel):
    """Shared fields for anything that is essentially a logo with a name."""

    name = models.CharField(max_length=80, help_text="Shown as a tooltip and to screen readers.")
    logo = models.FileField(
        upload_to="logos/",
        validators=[
            FileExtensionValidator(constants.ALLOWED_IMAGE_EXTENSIONS),
            validate_image_upload_size,
        ],
        help_text=constants.RECOMMENDED_BADGE_SIZE,
    )
    alt_text = models.CharField(
        max_length=160,
        blank=True,
        help_text="Description for screen readers. Defaults to the name if left blank.",
    )
    website_url = models.URLField(blank=True, help_text="Optional link when the logo is clicked.")
    is_active = models.BooleanField(default=True, help_text="Untick to hide without deleting.")

    class Meta(OrderableModel.Meta):
        abstract = True

    def __str__(self) -> str:
        return self.name

    @property
    def alt(self) -> str:
        """Alt text with a sensible fallback.

        Returns:
            ``alt_text`` or the name.
        """
        return self.alt_text or self.name


class TrustBadge(LogoModelBase):
    """An accreditation such as F-Gas, REFCOM, SafeContractor, CHAS or ISO 9001.

    Badges default to inactive so the site never claims an accreditation the company
    does not hold. Switch each one on in the admin once the certificate is in hand.
    """

    short_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="One line explaining why this matters, e.g. 'Legally required to handle "
        "refrigerant gases.' Shown on the About page.",
    )
    certificate_url = models.URLField(
        blank=True,
        help_text="Link to the public certificate or register entry, if there is one.",
    )
    certificate_number = models.CharField(
        max_length=60, blank=True, help_text="Shown on the About page if filled in."
    )
    show_in_header = models.BooleanField(
        default=False,
        help_text="Show as the small compliance mark next to the phone number in the sticky "
        "header. Tick this for F-Gas only.",
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Off by default. Only switch on accreditations you currently hold.",
    )

    class Meta(LogoModelBase.Meta):
        verbose_name = "Accreditation badge"
        verbose_name_plural = "Accreditation badges"


class BrandServiced(LogoModelBase):
    """A manufacturer whose equipment the company installs and maintains."""

    class Meta(LogoModelBase.Meta):
        verbose_name = "Brand we service"
        verbose_name_plural = "Brands we service"


class ClientLogo(LogoModelBase):
    """A customer logo shown in the trust strip. Get written permission before adding."""

    class Meta(LogoModelBase.Meta):
        verbose_name = "Client logo"
        verbose_name_plural = "Client logos"


class IntentCard(OrderableModel, TimeStampedModel):
    """One of the large 'I need…' tap targets under the homepage hero."""

    label = models.CharField(
        max_length=30, help_text="Large word on the tile, e.g. 'Repair'. Under 20 characters."
    )
    description = models.CharField(
        max_length=120,
        help_text="One short line under the label, e.g. 'Something has stopped working.'",
    )
    icon = models.CharField(
        max_length=30,
        choices=constants.ICON_CHOICES,
        default="wrench",
        help_text="Pick the icon drawn on the tile.",
    )
    url = models.CharField(
        max_length=200,
        help_text="Where the tile goes, e.g. /emergency-callout/ or /quote/.",
    )
    is_emergency = models.BooleanField(
        default=False,
        help_text="Tick for the emergency tile: it gets the orange action styling.",
    )
    is_active = models.BooleanField(default=True)

    class Meta(OrderableModel.Meta):
        verbose_name = "'I need…' tile"
        verbose_name_plural = "'I need…' tiles"

    def __str__(self) -> str:
        return self.label
