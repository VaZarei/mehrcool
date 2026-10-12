"""Module-level constants shared across the core app (no magic strings in code)."""

SITE_SETTINGS_PK = 1
SITE_SETTINGS_CACHE_KEY = "core:site_settings:v1"
NAVIGATION_CACHE_KEY = "core:navigation:v1"
CACHE_TIMEOUT_SECONDS = 60 * 60

RECOMMENDED_LOGO_SIZE = (
    "Recommended: SVG, or PNG at least 600 × 200 px with a transparent background."
)
RECOMMENDED_HERO_POSTER_SIZE = "Recommended: JPG or WebP, 1920 × 1080 px, under 250 KB."
RECOMMENDED_OG_IMAGE_SIZE = "Recommended: JPG or PNG, exactly 1200 × 630 px, under 300 KB."
RECOMMENDED_BADGE_SIZE = "Recommended: SVG or PNG, at least 320 px wide, transparent background."
RECOMMENDED_CARD_IMAGE_SIZE = "Recommended: JPG or WebP, 1600 × 1000 px (16:10), under 300 KB."
RECOMMENDED_FAVICON_SIZE = "Recommended: SVG, or PNG at 512 × 512 px."
RECOMMENDED_QR_SIZE = "Recommended: PNG or SVG, square, at least 800 × 800 px."

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "avif", "svg"]
ALLOWED_VIDEO_EXTENSIONS_MP4 = ["mp4"]
ALLOWED_VIDEO_EXTENSIONS_WEBM = ["webm"]

# Named inline SVG icons available to admins (rendered by the ``{% icon %}`` tag).
ICON_CHOICES = [
    ("wrench", "Wrench (repair)"),
    ("calendar-check", "Calendar with tick (maintenance)"),
    ("plus-square", "Plus in square (new installation)"),
    ("snowflake", "Snowflake (refrigeration)"),
    ("wind", "Airflow (air conditioning)"),
    ("bolt", "Lightning bolt (emergency)"),
    ("shield-check", "Shield with tick (compliance)"),
    ("clock", "Clock (response time)"),
    ("phone", "Phone"),
    ("map-pin", "Map pin"),
    ("thermometer", "Thermometer"),
    ("building", "Building"),
]
