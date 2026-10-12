"""URL patterns for sectors and case studies."""

from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("sectors/", views.SectorListView.as_view(), name="sector_list"),
    path("sectors/<slug:slug>/", views.SectorDetailView.as_view(), name="sector"),
    path("case-studies/", views.CaseStudyListView.as_view(), name="case_study_list"),
    path("case-studies/<slug:slug>/", views.CaseStudyDetailView.as_view(), name="case_study"),
]
