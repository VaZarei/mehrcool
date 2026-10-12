"""URL patterns for services: flat, keyword-rich paths."""

from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("services/", views.ServiceIndexView.as_view(), name="index"),
    path("<slug:category_slug>/<slug:slug>/", views.service_detail, name="detail"),
    # Category hubs share ``/<slug>/`` with pages; see apps.core.views.slug_dispatch.
    path("<slug:category_slug>/", views.category_view, name="category"),
]
