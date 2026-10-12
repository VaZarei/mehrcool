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
STYLEGUIDE_ENABLED = False  # never expose the internal styleguide in production

if not env("EMAIL_URL", default="") or env("EMAIL_URL", default="").startswith(("console", "dummy")):
    raise ImproperlyConfigured("EMAIL_URL must point at a real SMTP provider in production.")
_hosts = env("ALLOWED_HOSTS", default=[])
if not _hosts or any(h.strip() in ("*", ".*") or h.strip().startswith("*") for h in _hosts):
    raise ImproperlyConfigured("ALLOWED_HOSTS must list your real domains (no wildcards) in production.")
if any(h in ("localhost", "127.0.0.1", "[::1]", "testserver") for h in _hosts):
    raise ImproperlyConfigured("ALLOWED_HOSTS must not contain local hosts in production.")
_origins = env("CSRF_TRUSTED_ORIGINS", default=[])
if not _origins or not all(o.startswith("https://") and "*" not in o for o in _origins):
    raise ImproperlyConfigured(
        "CSRF_TRUSTED_ORIGINS must be set to explicit https:// origins in production, "
        "e.g. https://mehrcoolrefrigeration.co.uk"
    )

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
        # Rate-limit counters share this table; keep room so they are not culled early.
        "OPTIONS": {"MAX_ENTRIES": 10000, "CULL_FREQUENCY": 4},
    }
}

# Logs go to stdout (journald/Docker/host handles rotation). Set LOG_FILE to also write a
# size-rotated file; the directory must be readable only by the app user (chmod 700).
_log_handlers = ["console"]
_log_config = {"console": {"class": "logging.StreamHandler"}}
if env("LOG_FILE", default=""):
    _log_config["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": env("LOG_FILE"),
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 10,
        "encoding": "utf-8",
    }
    _log_handlers.append("file")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": _log_config,
    "root": {"handlers": _log_handlers, "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": _log_handlers, "level": "WARNING", "propagate": False},
    },
}
