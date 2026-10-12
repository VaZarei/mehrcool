"""URL patterns for the pages app.

The ``/<slug>/`` route is shared with service category hubs, so it is handled by
``apps.core.views.slug_dispatch`` and registered here under the ``pages`` namespace
so ``Page.get_absolute_url`` can reverse it.
"""

from django.urls import path

from apps.core.views import slug_dispatch

app_name = "pages"

urlpatterns = [
    path("<slug:slug>/", slug_dispatch, name="detail"),
]
