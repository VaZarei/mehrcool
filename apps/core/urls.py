"""URL patterns for the core app."""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("contact-card.vcf", views.vcard_download, name="vcard"),
    path("contact-card-qr.svg", views.vcard_qr, name="vcard_qr"),
    path("styleguide/", views.StyleguideView.as_view(), name="styleguide"),
]
