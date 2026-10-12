"""The ``SiteSettings`` singleton: every site-wide word, number, image and link."""

from __future__ import annotations

import re
from urllib.parse import quote

from django.core.cache import cache
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.core import constants
from apps.core.validators import (
    ImageDimensionValidator,
    validate_image_upload_size,
    validate_video_upload_size,
)

from .base import TimeStampedModel


def normalise_phone_for_href(phone: str) -> str:
    """Strip everything except digits and a leading ``+`` for ``tel:`` / WhatsApp links.

    Args:
        phone: Human-formatted phone number such as ``'+44 77 7888 9080'``.

    Returns:
        Digits-only string, keeping a leading ``+`` (e.g. ``'+447778889080'``).
    """
    phone = phone.strip()
    plus = "+" if phone.startswith("+") else ""
    return plus + re.sub(r"\D", "", phone)


class SiteSettings(TimeStampedModel):
    """Singleton holding all site-wide configuration editable from the admin.

    Always fetch it via :meth:`SiteSettings.load` which caches the row.
    """

    # --- Identity --------------------------------------------------------------------
    trading_name = models.CharField(
        max_length=120,
        default="Mehr Cool Refrigeration & Air Conditioning",
        help_text="The name visitors see everywhere: header, footer, page titles.",
    )
    legal_name = models.CharField(
        max_length=160,
        default="MEHR COOL REFRIGERATION & AIR CONDITIONING LTD",
        help_text="Registered company name, shown in the footer and legal pages.",
    )
    company_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Companies House number, shown in the footer (e.g. 15733975).",
    )
    vat_number = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional. Shown in the footer if filled in.",
    )
    founded_date = models.DateField(
        null=True,
        blank=True,
        help_text="Used in search-engine structured data and the About page.",
    )
    logo_light = models.FileField(
        upload_to="branding/",
        blank=True,
        validators=[
            FileExtensionValidator(constants.ALLOWED_IMAGE_EXTENSIONS),
            validate_image_upload_size,
        ],
        verbose_name="Logo (for light backgrounds)",
        help_text="Full-colour logo used in the header. " + constants.RECOMMENDED_LOGO_SIZE,
    )
    logo_dark = models.FileField(
        upload_to="branding/",
        blank=True,
        validators=[
            FileExtensionValidator(constants.ALLOWED_IMAGE_EXTENSIONS),
            validate_image_upload_size,
        ],
        verbose_name="Logo (for dark backgrounds)",
        help_text="White/light logo used in the footer and over the hero video. "
        + constants.RECOMMENDED_LOGO_SIZE,
    )
    favicon = models.FileField(
        upload_to="branding/",
        blank=True,
        validators=[
            FileExtensionValidator(constants.ALLOWED_IMAGE_EXTENSIONS + ["ico"]),
            validate_image_upload_size,
        ],
        help_text="Small icon shown in browser tabs. " + constants.RECOMMENDED_FAVICON_SIZE,
    )

    # --- Contact ---------------------------------------------------------------------
    primary_phone = models.CharField(
        max_length=30,
        default="+44 77 7888 9080",
        help_text="Main office number, shown in the header and footer. "
        "Type it exactly as you want it displayed, e.g. +44 77 7888 9080.",
    )
    emergency_phone = models.CharField(
        max_length=30,
        default="+44 77 7888 9080",
        help_text="24/7 emergency line. Every orange 'Call' button on the site dials this.",
    )
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        default="+44 77 7888 9080",
        help_text="Number behind the 'WhatsApp us' button. Leave blank to hide WhatsApp buttons.",
    )
    whatsapp_prefill_message = models.CharField(
        max_length=200,
        blank=True,
        default="Hi Mehr Cool, I need help with my refrigeration / air conditioning. "
        "Here is a photo of the unit and error code:",
        help_text="Text pre-typed into WhatsApp when a visitor taps the button. "
        "Managers usually reply with a photo of the error code.",
    )
    email = models.EmailField(
        default="info@mehrcoolrefrigeration.co.uk",
        help_text="Public email address shown in the footer and contact page.",
    )
    lead_notification_email = models.EmailField(
        blank=True,
        help_text="Where new enquiries and emergency callbacks are emailed. "
        "Leave blank to use the public email above.",
    )

    # --- Address ---------------------------------------------------------------------
    address_line_1 = models.CharField(max_length=120, default="Dept 2710, 126 East Ferry Road")
    address_line_2 = models.CharField(max_length=120, blank=True, default="Canary Wharf")
    city = models.CharField(max_length=80, default="London")
    region = models.CharField(
        max_length=80,
        default="England",
        help_text="County or region, used in structured data.",
    )
    postcode = models.CharField(max_length=12, default="E14 9FP")
    country_code = models.CharField(
        max_length=2,
        default="GB",
        help_text="Two-letter country code (GB).",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        default="51.491200",
        help_text="Used for the map and local search results.",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        default="-0.015100",
    )
    google_maps_embed_url = models.URLField(
        max_length=600,
        blank=True,
        help_text="Paste the 'src' URL from Google Maps → Share → Embed a map. "
        "Leave blank to hide the map.",
    )
    areas_served = models.CharField(
        max_length=200,
        default="London, Greater London, Berkshire",
        help_text="Comma-separated list used in the footer and structured data.",
    )

    # --- Hours & service promise -----------------------------------------------------
    opening_hours_text = models.CharField(
        max_length=120,
        default="Open 24 hours a day, 365 days a year",
        help_text="Plain-English hours line shown in the header strip and footer.",
    )
    is_open_24_7 = models.BooleanField(
        default=True,
        verbose_name="Open 24/7",
        help_text="Tells search engines you are open around the clock.",
    )
    response_time_claim = models.CharField(
        max_length=90,
        default="Engineer on site in under 2 hours across London",
        help_text="The response-time promise shown in the hero and emergency page. "
        "Keep it under 60 characters and make sure you can honour it.",
    )
    price_range = models.CharField(
        max_length=5,
        default="£££",
        help_text="Rough price band shown to search engines, e.g. ££ or £££.",
    )

    # --- Emergency banner ------------------------------------------------------------
    emergency_banner_enabled = models.BooleanField(
        default=True,
        help_text="Show the thin strip above the header with the emergency number and hours.",
    )
    emergency_banner_text = models.CharField(
        max_length=120,
        default="24/7 emergency refrigeration & air conditioning engineers across London",
        help_text="Text in the strip above the header. Keep it under 80 characters.",
    )

    # --- Homepage hero ---------------------------------------------------------------
    hero_headline = models.CharField(
        max_length=90,
        default="Commercial refrigeration and air conditioning, kept running.",
        help_text="Main headline over the homepage video. Under 60 characters is ideal so it "
        "does not wrap to three lines on mobile.",
    )
    hero_subheadline = models.CharField(
        max_length=200,
        default="F-Gas certified engineers for cold rooms, display fridges, cellar cooling and "
        "VRF air conditioning. Installation, planned maintenance and 24/7 emergency repair.",
        help_text="One or two sentences under the headline.",
    )
    hero_primary_cta_label = models.CharField(
        max_length=40,
        default="Call the 24/7 emergency line",
        help_text="Label on the orange button. It always dials the emergency phone number.",
    )
    hero_secondary_cta_label = models.CharField(
        max_length=40,
        default="Request a quote",
        help_text="Label on the outlined button.",
    )
    hero_secondary_cta_url = models.CharField(
        max_length=200,
        default="/quote/",
        help_text="Where the outlined button goes. Usually /quote/ or /contact/.",
    )
    hero_video_mp4 = models.FileField(
        upload_to="hero/",
        blank=True,
        validators=[
            FileExtensionValidator(constants.ALLOWED_VIDEO_EXTENSIONS_MP4),
            validate_video_upload_size,
        ],
        verbose_name="Hero video (MP4)",
        help_text="Silent background video, H.264 MP4, 1920 × 1080, 10–20 seconds, under 8 MB. "
        "Not downloaded on phones — the poster image is shown instead.",
    )
    hero_video_webm = models.FileField(
        upload_to="hero/",
        blank=True,
        validators=[
            FileExtensionValidator(constants.ALLOWED_VIDEO_EXTENSIONS_WEBM),
            validate_video_upload_size,
        ],
        verbose_name="Hero video (WebM)",
        help_text="Optional smaller WebM version of the same clip for browsers that support it.",
    )
    hero_poster = models.ImageField(
        upload_to="hero/",
        blank=True,
        validators=[validate_image_upload_size, ImageDimensionValidator(1200, 675)],
        help_text="Still image shown instantly before the video loads, and instead of the video "
        "on phones. " + constants.RECOMMENDED_HERO_POSTER_SIZE,
    )
    hero_poster_alt = models.CharField(
        max_length=160,
        blank=True,
        default="Mehr Cool engineer servicing a commercial refrigeration condenser",
        help_text="Describe the poster image for screen readers.",
    )
    intent_strip_heading = models.CharField(
        max_length=60,
        default="I need…",
        help_text="Heading above the three 'Repair / Maintenance / Installation' tiles.",
    )

    # --- Homepage sections -----------------------------------------------------------
    home_services_heading = models.CharField(
        max_length=80,
        default="What we do",
        help_text="Heading above the services grid on the homepage.",
    )
    home_services_intro = models.CharField(
        max_length=540,
        blank=True,
        default="Design, installation, planned maintenance and repair for commercial cooling — "
        "one contractor, one point of contact, one set of compliance records.",
        help_text="One sentence under the heading.",
    )
    home_why_heading = models.CharField(
        max_length=80,
        default="Why facilities teams keep us on speed dial",
        help_text="Heading for the 'why choose us' section.",
    )
    home_why_items = models.TextField(
        blank=True,
        default=(
            "Engineers, not sales reps :: The person who answers the phone is the person who "
            "knows what a high-pressure trip means at 2am.\n"
            "F-Gas compliant by default :: Refrigerant recovered, weighed and logged on every "
            "job, with certificates for your records.\n"
            "Fixed-price PPM contracts :: Scheduled visits, filter changes, leak checks and "
            "temperature logs — priced per asset, no surprises.\n"
            "Multi-brand, manufacturer-trained :: Daikin, Mitsubishi Electric, Toshiba and "
            "Fujitsu systems installed and maintained to spec."
        ),
        help_text="One item per line in the form: Title :: Description",
    )
    home_proof_heading = models.CharField(
        max_length=80,
        default="Recent work",
        help_text="Heading above the featured case studies.",
    )
    home_reviews_heading = models.CharField(
        max_length=80,
        default="What clients say",
        help_text="Heading above the reviews.",
    )

    # --- Reusable CTA band -------------------------------------------------------------
    cta_band_title = models.CharField(
        max_length=90,
        default="Talk to an engineer, not a call centre",
        help_text="Heading on the navy call-to-action band at the bottom of most pages.",
    )
    cta_band_text = models.CharField(
        max_length=240,
        default="Call now for a breakdown, or send us the site details and we will come back "
        "with a fixed-price quote.",
        help_text="Sentence under the heading in the call-to-action band.",
    )
    cta_band_checklist = models.TextField(
        blank=True,
        default=(
            "F-Gas certified engineers — refrigerant handling logged on every job\n"
            "Written quotes and service reports for every site\n"
            "Public liability insurance and RAMS supplied on request"
        ),
        help_text="One line per tick item shown beside the button. Hours and company number "
        "are added automatically.",
    )

    # --- Microcopy for fixed UI --------------------------------------------------------
    mobile_bar_call_label = models.CharField(
        max_length=30,
        default="Call engineer now",
        help_text="Label on the bottom-of-screen call button on phones.",
    )
    mobile_bar_whatsapp_label = models.CharField(
        max_length=30,
        default="WhatsApp us",
        help_text="Label on the bottom-of-screen WhatsApp button on phones.",
    )
    footer_contact_heading = models.CharField(
        max_length=40,
        default="Talk to an engineer",
        help_text="Heading above the contact details in the footer.",
    )
    qr_card_title = models.CharField(
        max_length=80,
        default="Save our number before you need it",
        help_text="Heading on the QR 'save our contact' card.",
    )

    # --- Contact card / QR -----------------------------------------------------------
    contact_qr_image = models.FileField(
        upload_to="branding/",
        blank=True,
        validators=[
            FileExtensionValidator(constants.ALLOWED_IMAGE_EXTENSIONS),
            validate_image_upload_size,
        ],
        verbose_name="'Save our contact' QR code",
        help_text="Upload your designed QR code. If left blank the site generates one from the "
        "details above. " + constants.RECOMMENDED_QR_SIZE,
    )
    contact_qr_caption = models.CharField(
        max_length=120,
        default="Scan to save our 24/7 number to your phone",
        help_text="Short line shown under the QR code.",
    )

    # --- Social ----------------------------------------------------------------------
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True, verbose_name="X (Twitter) URL")
    google_business_url = models.URLField(
        blank=True,
        help_text="Link to your Google Business Profile — used by the 'Read our reviews' link.",
    )
    checkatrade_url = models.URLField(blank=True)

    # --- Analytics -------------------------------------------------------------------
    ga4_measurement_id = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Google Analytics 4 measurement ID",
        help_text="Looks like G-XXXXXXXXXX. Leave blank to disable.",
    )
    gtm_container_id = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Google Tag Manager container ID",
        help_text="Looks like GTM-XXXXXXX. Leave blank to disable.",
    )

    # --- Search engines --------------------------------------------------------------
    default_meta_title_suffix = models.CharField(
        max_length=60,
        default=" | Mehr Cool Refrigeration & Air Conditioning, London",
        help_text="Added to the end of every page title in Google unless a page sets its own.",
    )
    default_meta_description = models.CharField(
        max_length=160,
        default="Commercial refrigeration, walk-in cold room installation, VRF air conditioning "
        "and 24/7 emergency maintenance across London and surrounding areas.",
        help_text="Used by Google when a page has no description of its own. Max 160 characters.",
    )
    default_og_image = models.ImageField(
        upload_to="branding/",
        blank=True,
        validators=[validate_image_upload_size],
        verbose_name="Default social sharing image",
        help_text="Shown when a page is shared on LinkedIn/WhatsApp/Facebook. "
        + constants.RECOMMENDED_OG_IMAGE_SIZE,
    )
    google_rating_override = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Your live Google star rating (e.g. 4.9). Leave blank to calculate from the "
        "reviews entered under Testimonials.",
    )
    google_review_count_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Your total Google review count. Leave blank to count the reviews entered "
        "under Testimonials.",
    )

    # --- Footer ----------------------------------------------------------------------
    footer_blurb = models.TextField(
        max_length=400,
        default="Independent commercial refrigeration and air conditioning contractor based in "
        "Canary Wharf. F-Gas certified engineers covering London, Greater London and "
        "Berkshire, 24 hours a day.",
        help_text="Short paragraph under the logo in the footer.",
    )
    footer_legal_line = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional extra line in the footer, e.g. 'Registered in England and Wales.'",
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:
        return "Site settings"

    def save(self, *args: object, **kwargs: object) -> None:
        """Force the singleton primary key and bust the cache on save."""
        self.pk = constants.SITE_SETTINGS_PK
        super().save(*args, **kwargs)
        cache.delete(constants.SITE_SETTINGS_CACHE_KEY)

    def delete(self, *args: object, **kwargs: object) -> None:  # type: ignore[override]
        """Deleting the singleton is not allowed; silently ignore."""
        return None

    @classmethod
    def load(cls) -> SiteSettings:
        """Return the singleton, creating it with defaults if missing. Cached.

        Returns:
            The single ``SiteSettings`` row.
        """
        obj = cache.get(constants.SITE_SETTINGS_CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=constants.SITE_SETTINGS_PK)
            cache.set(constants.SITE_SETTINGS_CACHE_KEY, obj, constants.CACHE_TIMEOUT_SECONDS)
        return obj

    # --- Derived helpers used by templates and schema --------------------------------
    @property
    def emergency_tel_href(self) -> str:
        """``tel:`` link for the emergency line.

        Returns:
            A string such as ``'tel:+447778889080'``.
        """
        return f"tel:{normalise_phone_for_href(self.emergency_phone)}"

    @property
    def primary_tel_href(self) -> str:
        """``tel:`` link for the office line.

        Returns:
            A string such as ``'tel:+447778889080'``.
        """
        return f"tel:{normalise_phone_for_href(self.primary_phone)}"

    @property
    def whatsapp_href(self) -> str:
        """``wa.me`` deep link with the pre-filled message, or ``''`` if disabled.

        Returns:
            WhatsApp click-to-chat URL.
        """
        if not self.whatsapp_number:
            return ""
        digits = normalise_phone_for_href(self.whatsapp_number).lstrip("+")
        text = quote(self.whatsapp_prefill_message) if self.whatsapp_prefill_message else ""
        return f"https://wa.me/{digits}" + (f"?text={text}" if text else "")

    @property
    def notification_recipient(self) -> str:
        """Email address that receives lead notifications.

        Returns:
            The override address if set, otherwise the public email.
        """
        return self.lead_notification_email or self.email

    @property
    def full_address_lines(self) -> list[str]:
        """Address as a list of non-empty lines for display.

        Returns:
            Ordered address lines.
        """
        return [
            line
            for line in (self.address_line_1, self.address_line_2, self.city, self.postcode)
            if line
        ]

    @property
    def areas_served_list(self) -> list[str]:
        """Areas served as a clean list.

        Returns:
            Stripped, non-empty area names.
        """
        return [a.strip() for a in self.areas_served.split(",") if a.strip()]

    @property
    def cta_checklist(self) -> list[str]:
        """CTA band tick items as a list.

        Returns:
            Non-empty lines.
        """
        return [line.strip() for line in self.cta_band_checklist.splitlines() if line.strip()]

    @property
    def why_items(self) -> list[dict[str, str]]:
        """Parsed 'why choose us' items.

        Returns:
            Dicts with ``title``/``body``/``url`` keys.
        """
        from apps.pages.services import parse_block_items

        return parse_block_items(self.home_why_items)

    @property
    def has_hero_video(self) -> bool:
        """Whether at least one hero video source has been uploaded.

        Returns:
            ``True`` if MP4 or WebM exists.
        """
        return bool(self.hero_video_mp4 or self.hero_video_webm)
