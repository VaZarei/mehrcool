"""Local development settings: SQLite, console email, debug toolbar, styleguide on."""

from .base import *  # noqa: F403
from .base import BASE_DIR, INSTALLED_APPS, MIDDLEWARE, STORAGES

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1","10.161.51.41", "[::1]", "testserver"]
STYLEGUIDE_ENABLED = True

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.common.CommonMiddleware"),
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)
INTERNAL_IPS = ["127.0.0.1"]
DEBUG_TOOLBAR_CONFIG = {"SHOW_COLLAPSED": True}

# Plain storage locally so templates render without running collectstatic.
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
