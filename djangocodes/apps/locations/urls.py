"""URL patterns for service areas."""

from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("areas/", views.AreaListView.as_view(), name="index"),
    path(
        "areas/air-conditioning-refrigeration-<slug:slug>/",
        views.AreaDetailView.as_view(),
        name="detail",
    ),
]
