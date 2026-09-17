"""Shared Django settings for the Mehr Cool website.

Every value that differs between environments is read from the environment via
``django-environ``. Nothing secret lives in this file.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    SITE_URL=(str, "https://mehrcoolrefrigeration.co.uk"),
    LEAD_NOTIFICATION_EMAIL=(str, "info@mehrcoolrefrigeration.co.uk"),
    DEFAULT_FROM_EMAIL=(str, "Mehr Cool Website <noreply@mehrcoolrefrigeration.co.uk>"),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-only-key-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

SITE_ID = 1
SITE_URL = env("SITE_URL").rstrip("/")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.redirects",
    "django.contrib.humanize",
    "django.forms",
]

PROJECT_APPS = [
    "apps.core",
    "apps.seo",
    "apps.pages",
    "apps.services",
    "apps.projects",
    "apps.locations",
    "apps.testimonials",
    "apps.leads",
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
                "apps.core.context_processors.navigation",
            ],
            "builtins": ["apps.core.templatetags.core_tags"],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "admin:login"

# ---------------------------------------------------------------------------
# Internationalisation — British English, London time
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365
WHITENOISE_ROOT = BASE_DIR / "static" / "root"

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
vars().update(env.email_url("EMAIL_URL", default="consolemail://"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
LEAD_NOTIFICATION_EMAIL = env("LEAD_NOTIFICATION_EMAIL")

# ---------------------------------------------------------------------------
# Caching (template fragment caching for header / footer / nav)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mehrcool",
    }
}
FRAGMENT_CACHE_SECONDS = 60 * 15

# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
MAX_UPLOAD_IMAGE_BYTES = 5 * 1024 * 1024
MAX_UPLOAD_VIDEO_BYTES = 12 * 1024 * 1024

# ---------------------------------------------------------------------------
# Security defaults (tightened further in production.py)
# ---------------------------------------------------------------------------
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # HTMX needs to read the token from the cookie/meta tag.

# ---------------------------------------------------------------------------
# Project-specific
# ---------------------------------------------------------------------------
STYLEGUIDE_ENABLED = env.bool("STYLEGUIDE_ENABLED", default=False)
# Used only by the 500 page when the database itself is unreachable.
EMERGENCY_PHONE_FALLBACK = env("EMERGENCY_PHONE_FALLBACK", default="+44 77 7888 9080")
TRADING_NAME_FALLBACK = env(
    "TRADING_NAME_FALLBACK", default="Mehr Cool Refrigeration & Air Conditioning"
)
