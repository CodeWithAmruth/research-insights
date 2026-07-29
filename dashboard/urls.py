from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("documents/", views.DocumentTypesView.as_view(), name="documents"),
    path(
        "document/<document_type>/",
        views.DocumentTypeDetailView.as_view(),
        name="document_type_detail",
    ),
    path("authors/", views.AuthorsView.as_view(), name="authors"),
    path(
        "authors/<first_name>/<last_name>/",
        views.AuthorDetailView.as_view(),
        name="author_detail",
    ),
    path("journals/", views.JournalsView.as_view(), name="journals"),
    path(
        "journal/<journal_id>/",
        views.JournalDetailView.as_view(),
        name="journal_detail",
    ),
    path("departments/", views.DepartmentsView.as_view(), name="departments"),
    path(
        "departments/<int:pk>/",
        views.DepartmentDetailView.as_view(),
        name="department_detail",
    ),
    path("collaboration/", views.CollaborationView.as_view(), name="collaboration"),
    path(
        "collaboration/<path:collaboration_type>/",
        views.CollaborationDetailView.as_view(),
        name="collaboration_detail",
    ),
    path("trends/", views.TrendsView.as_view(), name="trends"),
    path(
        "trends/<int:year>/",
        views.TrendYearDetailView.as_view(),
        name="trend_year_detail",
    ),
    path("impact/", views.ImpactView.as_view(), name="impact"),
    path(
        "impact/<int:journal_id>/",
        views.ImpactDetailView.as_view(),
        name="impact_detail",
    ),
    path("rri/role/", views.RRIRoleView.as_view(), name="rri_role"),
    path(
        "rri-role/<path:role>/",
        views.RRIRoleDetailView.as_view(),
        name="rri_role_detail",
    ),
    path(
        "country/collaboration/",
        views.CountryCollaborationView.as_view(),
        name="country_collaboration",
    ),
    path(
        "country-collaboration/<path:country>/",
        views.CountryCollaborationDetailView.as_view(),
        name="country_collaboration_detail",
    ),
    path(
        "institution/collaboration/",
        views.InstitutionCollaborationView.as_view(),
        name="institution_collaboration",
    ),
    path(
        "institution-collaboration/<path:institution>/",
        views.InstitutionCollaborationDetailView.as_view(),
        name="institution_collaboration_detail",
    ),
]
