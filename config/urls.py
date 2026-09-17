"""Root URL configuration.

Order matters: explicit paths first, then app namespaces, and finally the shared
``/<slug>/`` dispatcher that serves both category hubs and content pages.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView

from apps.seo.sitemaps import SITEMAPS
from apps.seo.views import robots_txt

handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "quote/", RedirectView.as_view(pattern_name="leads:contact", permanent=False), name="quote"
    ),
    path("", include("apps.core.urls")),
    path("", include("apps.leads.urls")),
    path("", include("apps.projects.urls")),
    path("", include("apps.locations.urls")),
    path("", include("apps.services.urls")),
    path("", include("apps.pages.urls")),
]

if settings.DEBUG:
    from django.views import defaults

    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
        path("404/", defaults.page_not_found, {"exception": Exception("Preview")}),
        path("500/", defaults.server_error),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *urlpatterns,
    ]
