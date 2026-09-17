"""Friendlier admin for URL redirects (uses Django's built-in redirects app)."""

from django.contrib import admin
from django.contrib.redirects.admin import RedirectAdmin as DjangoRedirectAdmin
from django.contrib.redirects.models import Redirect

admin.site.unregister(Redirect)


@admin.register(Redirect)
class RedirectAdmin(DjangoRedirectAdmin):
    """Redirects with plain-English guidance."""

    fieldsets = (
        (
            None,
            {
                "fields": ("site", "old_path", "new_path"),
                "description": "Use this when you rename a page so old links and Google results "
                "still work. Old path must start with a slash, e.g. /old-page/. New path can be "
                "a slash path or a full https:// address. Leave New path empty to return "
                "'410 Gone'.",
            },
        ),
    )
