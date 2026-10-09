"""Production settings: PostgreSQL, hashed static files, strict security headers."""

from django.core.exceptions import ImproperlyConfigured
from django.utils.csp import CSP

from .base import *  # noqa: F403
from .base import SECRET_KEY, env

if len(SECRET_KEY) < 50 or SECRET_KEY.lower().startswith(("insecure", "change", "django-insecure")):
    raise ImproperlyConfigured(
        "SECRET_KEY must be set in the environment to a unique random value of at least 50 "
        "characters. Generate one with: python -c "
        '"from django.core.management.utils import get_random_secret_key as g; print(g())"'
    )

DEBUG = False

if not env("EMAIL_URL", default="") or env("EMAIL_URL", default="").startswith(("console", "dummy")):
    raise ImproperlyConfigured("EMAIL_URL must point at a real SMTP provider in production.")
if not env("ALLOWED_HOSTS", default=[]):
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")

# Behind Cloudflare / a TLS-terminating proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Content-Security-Policy. Inline scripts carry a per-request nonce ({{ csp_nonce }}).
# Inline styles stay allowed because templates use style="" attributes.
_GOOGLE_ANALYTICS = [
    "https://www.google-analytics.com",
    "https://*.google-analytics.com",
    "https://*.analytics.google.com",
    "https://www.googletagmanager.com",
]
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [
        CSP.SELF,
        CSP.NONCE,
        "https://www.googletagmanager.com",
        "https://www.google-analytics.com",
    ],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],
    "img-src": [CSP.SELF, "data:", "blob:", "https:"],
    "font-src": [CSP.SELF, "data:"],
    "media-src": [CSP.SELF, "blob:"],
    "connect-src": [CSP.SELF, *_GOOGLE_ANALYTICS],
    "frame-src": [
        "https://www.googletagmanager.com",
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.youtube-nocookie.com",
        "https://player.vimeo.com",
    ],
    "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
}

# Cloudflare caches static assets for a year because filenames are content-hashed.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
