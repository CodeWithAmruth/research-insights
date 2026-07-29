from django.shortcuts import render
from django.db.models import Count, Avg, Sum, Q
from django.contrib.auth.decorators import login_required

from .models import (
    Publication,
    Author,
    Affiliation,
)


# ---------- Helper: detect RRI affiliation ----------
def rri_filter():
    return Q(author_affiliations__affiliation__name__icontains="raman")


@login_required
def dashboard(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    publications = Publication.objects.filter(
        authors__author_affiliations__affiliation__name__icontains="raman"
    ).distinct()

    # ---------- Date filter ----------
    if start_date and end_date:
        publications = publications.filter(date_published__range=[start_date, end_date])

    # ---------- BASIC METRICS ----------
    total_publications = publications.count()

    total_impact_factor = (
        publications.aggregate(total=Sum("journal__impact_factor"))["total"] or 0
    )

    avg_impact_factor = (
        total_impact_factor / total_publications if total_publications else 0
    )

    # ---------- DOCUMENT TYPE ----------
    by_document_type = (
        publications.values("document_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # ---------- COLLABORATION TYPE ----------
    by_collaboration = publications.values("collaboration_type").annotate(
        count=Count("id")
    )

    # ---------- RRI ROLE ----------
    by_rri_role = publications.values("authors__rri_role").annotate(
        count=Count("id", distinct=True)
    )

    avg_pub_per_role = publications.values("authors__rri_role").annotate(avg=Avg("id"))

    # ---------- DEPARTMENTS ----------
    by_department = publications.values("departments__name").annotate(
        count=Count("id", distinct=True)
    )

    # ---------- TOP AUTHORS ----------
    top_authors = (
        Author.objects.filter(author_affiliations__affiliation__name__icontains="raman")
        .annotate(pub_count=Count("publications", distinct=True))
        .order_by("-pub_count")[:10]
    )

    # ---------- COUNTRIES ----------
    top_countries = (
        Affiliation.objects.exclude(country__isnull=True)
        .exclude(country="")
        .filter(author_affiliations__publication__in=publications)
        .values("country")
        .annotate(count=Count("author_affiliations__publication", distinct=True))
        .order_by("-count")[:25]
    )

    # ---------- INSTITUTIONS ----------
    top_institutions = (
        Affiliation.objects.exclude(name__icontains="raman")
        .filter(author_affiliations__publication__in=publications)
        .values("name")
        .annotate(count=Count("author_affiliations__publication", distinct=True))
        .order_by("-count")[:25]
    )

    return render(
        request,
        "publications/dashboard/dashboard.html",
        {
            "total_publications": total_publications,
            "total_impact_factor": round(total_impact_factor, 2),
            "avg_impact_factor": round(avg_impact_factor, 2),
            "by_document_type": by_document_type,
            "by_collaboration": by_collaboration,
            "by_rri_role": by_rri_role,
            "avg_pub_per_role": avg_pub_per_role,
            "by_department": by_department,
            "top_authors": top_authors,
            "top_countries": top_countries,
            "top_institutions": top_institutions,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
