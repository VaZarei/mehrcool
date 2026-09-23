"""URL patterns for lead capture."""

from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("contact/thank-you/", views.ContactThanksView.as_view(), name="contact_thanks"),
    path("request/", views.RequestView.as_view(), name="request"),
    path("request/thank-you/", views.RequestThanksView.as_view(), name="request_thanks"),
    path("emergency-callout/", views.EmergencyView.as_view(), name="emergency"),
    path(
        "emergency-callout/thank-you/",
        views.EmergencyThanksView.as_view(),
        name="emergency_thanks",
    ),
]
