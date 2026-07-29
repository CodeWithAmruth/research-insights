from django.db.models import Count, Avg, Sum, Max, Prefetch, Min
from django.urls import reverse
from dashboard.filters import DynamicFilter
from publications.models import (
    Department,
    Journal,
    Publication,
    Author,
    AuthorAffiliation,
)
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from urllib.parse import unquote


class DashboardHomeView(TemplateView):
    template_name = "dashboard/dashboard.html"

    # -----------------------
    # DynamicFilter settings
    # -----------------------

    search_fields = [
        "title",
        "journal__name",
        "doi",
    ]

    gt_filters = []

    lt_filters = []

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    sortable_columns = [
        "date_published",
    ]

    date_filters = [
        "date_published",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = Publication.objects.select_related("journal").prefetch_related(
            "authors"
        )

        filterset = DynamicFilter(
            self.request.GET,
            queryset=queryset,
            view=self,
        )

        publications = filterset.qs

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            avg_impact_factor=Avg("journal__impact_factor"),
        )

        recent_publications = publications.annotate(
            author_count=Count("authors", distinct=True)
        ).order_by("-date_published")[:5]

        document_counts = list(
            publications.values("document_type")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        year_stats = list(
            publications.values("date_published__year")
            .annotate(total=Count("id"))
            .order_by("date_published__year")
        )

        context.update(
            {
                "filter": filterset,
                # KPI
                "total_publications": summary["total_publications"] or 0,
                "total_impact_factor": summary["total_impact_factor"] or 0,
                "avg_impact_factor": summary["avg_impact_factor"] or 0,
                "active_authors": (
                    Author.objects.filter(publications__in=publications)
                    .distinct()
                    .count()
                ),
                # Charts
                "document_counts": document_counts,
                "year_stats": year_stats,
                # Table
                "recent_publications": recent_publications,
            }
        )

        return context


# =====================================================
# DOCUMENT TYPES
# =====================================================
class DocumentTypesView(TemplateView):
    template_name = "dashboard/document_types.html"

    paginate_by = 10

    search_fields = [
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "date_published",
    ]

    gt_filters = []
    lt_filters = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        publications = Publication.objects.select_related("journal")

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        document_types = (
            publications.values("document_type")
            .annotate(
                total_publications=Count("id"),
                average_impact_factor=Avg("journal__impact_factor"),
                total_impact_factor=Sum("journal__impact_factor"),
            )
            .order_by("-total_publications")
        )

        paginator = Paginator(document_types, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "filter": filterset,
                # Table
                "page_obj": page_obj,
                # Charts
                "document_types_data": list(document_types),
                # KPI Cards
                "document_type_count": page_obj.paginator.count,
                "document_total_publications": summary["total_publications"] or 0,
                "document_total_impact": summary["total_impact_factor"] or 0,
                "document_average_impact": summary["average_impact_factor"] or 0,
                "document_highest_impact": summary["highest_impact_factor"] or 0,
                # Header
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Document Types",
                    },
                ],
            }
        )

        return context


class DocumentTypeDetailView(TemplateView):
    template_name = "dashboard/document_type_detail.html"

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        document_type = self.kwargs["document_type"]

        publications = (
            Publication.objects.filter(document_type=document_type)
            .select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .order_by("-date_published")
        )

        paginator = Paginator(
            publications,
            self.paginate_by,
        )

        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        yearly_data = (
            publications.values("date_published__year")
            .annotate(total=Count("id"))
            .order_by("date_published__year")
        )

        context.update(
            {
                "document_type": document_type,
                "page_obj": page_obj,
                "publication_trend_data": list(yearly_data),
                "total_publications": summary["total_publications"] or 0,
                "total_impact_factor": summary["total_impact_factor"] or 0,
                "average_impact_factor": summary["average_impact_factor"] or 0,
                "highest_impact_factor": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Document Types",
                        "url": reverse("dashboard:documents"),
                    },
                    {
                        "label": document_type,
                    },
                ],
            }
        )

        return context


# =====================================================
# AUTHORS
# =====================================================


class AuthorsView(TemplateView):
    template_name = "dashboard/authors.html"

    paginate_by = 10

    # -----------------------------
    # Search
    # -----------------------------
    search_fields = [
        "first_name",
        "last_name",
    ]

    date_filters = [
        "date_published",
    ]

    # -----------------------------
    # Sorting
    # -----------------------------
    sortable_columns = [
        "first_name",
        "last_name",
        "total_publications",
        "average_impact_factor",
        "total_impact_factor",
    ]

    # -----------------------------
    # Range filters
    # -----------------------------
    gt_filters = [
        "total_publications",
        "total_impact_factor",
        "average_impact_factor",
    ]

    lt_filters = [
        "total_publications",
        "total_impact_factor",
        "average_impact_factor",
    ]

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # --------------------------------------------------
        # Publications
        # --------------------------------------------------

        publications = Publication.objects.select_related("journal").prefetch_related(
            "authors"
        )

        # --------------------------------------------------
        # Authors Query
        # --------------------------------------------------

        authors = (
            Author.objects.filter(publications__in=publications)
            .annotate(
                total_publications=Count(
                    "publications",
                    distinct=True,
                ),
                total_impact_factor=Sum(
                    "publications__journal__impact_factor",
                ),
                average_impact_factor=Avg(
                    "publications__journal__impact_factor",
                ),
            )
            .prefetch_related(
                Prefetch(
                    "author_affiliations",
                    queryset=AuthorAffiliation.objects.select_related("affiliation"),
                )
            )
            .distinct()
        )

        # --------------------------------------------------
        # Merge duplicate authors
        # --------------------------------------------------

        merged_authors = {}

        for author in authors:
            key = (
                author.first_name.strip().lower(),
                author.last_name.strip().lower(),
            )

            if key not in merged_authors:
                author.merged_publications = author.total_publications or 0

                author.merged_impact = author.total_impact_factor or 0

                author.merged_affiliations = set()

                merged_authors[key] = author

            else:
                existing = merged_authors[key]

                existing.merged_publications += author.total_publications or 0

                existing.merged_impact += author.total_impact_factor or 0

            for affiliation in author.author_affiliations.all():
                merged_authors[key].merged_affiliations.add(
                    affiliation.affiliation.name
                )

        authors = list(merged_authors.values())

        # --------------------------------------------------
        # Final calculated values
        # --------------------------------------------------

        for author in authors:
            author.affiliations = list(author.merged_affiliations)

            author.affiliation_count = len(author.affiliations)

            author.total_publications = author.merged_publications

            author.total_impact_factor = author.merged_impact

            author.average_impact_factor = (
                author.merged_impact / author.merged_publications
                if author.merged_publications
                else 0
            )

        # --------------------------------------------------
        # Apply search AFTER merging
        # --------------------------------------------------

        search = self.request.GET.get("search", "").strip().lower()

        if search:
            authors = [
                author
                for author in authors
                if search in author.first_name.lower()
                or search in author.last_name.lower()
            ]

        # Greater than filters

        total_publications_gt = self.request.GET.get("total_publications_gt")

        if total_publications_gt:
            authors = [
                author
                for author in authors
                if author.total_publications > int(total_publications_gt)
            ]

        total_impact_gt = self.request.GET.get("total_impact_factor_gt")

        if total_impact_gt:
            authors = [
                author
                for author in authors
                if author.total_impact_factor > float(total_impact_gt)
            ]

        average_impact_gt = self.request.GET.get("average_impact_factor_gt")

        if average_impact_gt:
            authors = [
                author
                for author in authors
                if author.average_impact_factor > float(average_impact_gt)
            ]

        # Less than filters

        total_publications_lt = self.request.GET.get("total_publications_lt")

        if total_publications_lt:
            authors = [
                author
                for author in authors
                if author.total_publications < int(total_publications_lt)
            ]

        total_impact_lt = self.request.GET.get("total_impact_factor_lt")

        if total_impact_lt:
            authors = [
                author
                for author in authors
                if author.total_impact_factor < float(total_impact_lt)
            ]

        average_impact_lt = self.request.GET.get("average_impact_factor_lt")

        if average_impact_lt:
            authors = [
                author
                for author in authors
                if author.average_impact_factor < float(average_impact_lt)
            ]

        # Ordering

        ordering = self.request.GET.get("ordering")

        if ordering:
            reverse = ordering.startswith("-")

            field = ordering.replace("-", "")

            authors.sort(
                key=lambda x: getattr(x, field, ""),
                reverse=reverse,
            )

        # --------------------------------------------------
        # Pagination
        # --------------------------------------------------

        paginator = Paginator(authors, self.paginate_by)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        # --------------------------------------------------
        # Chart Data
        # Uses merged + filtered data
        # --------------------------------------------------

        authors_data = [
            {
                "authors__first_name": author.first_name,
                "authors__last_name": author.last_name,
                "total_publications": (author.total_publications),
                "total_impact_factor": float(author.total_impact_factor),
            }
            for author in authors[:10]
        ]

        # --------------------------------------------------
        # Summary
        # Based on merged authors
        # --------------------------------------------------

        summary = {
            "total_publications": sum(a.total_publications for a in authors),
            "total_impact_factor": sum(a.total_impact_factor for a in authors),
            "average_impact_factor": (
                sum(a.average_impact_factor for a in authors) / len(authors)
                if authors
                else 0
            ),
            "highest_impact_factor": max(
                (a.total_impact_factor for a in authors),
                default=0,
            ),
        }

        context.update(
            {
                "page_obj": page_obj,
                "author_count": len(authors),
                "authors_data": authors_data,
                "author_total_publications": (summary["total_publications"]),
                "author_total_impact": (summary["total_impact_factor"]),
                "author_average_impact": (summary["average_impact_factor"]),
                "author_highest_impact": (summary["highest_impact_factor"]),
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": "/dashboard/",
                    },
                    {
                        "label": "Authors",
                    },
                ],
            }
        )

        return context


class AuthorDetailView(TemplateView):
    template_name = "dashboard/author_detail.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        first_name = self.kwargs["first_name"]
        last_name = self.kwargs["last_name"]

        authors = Author.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
        ).prefetch_related(
            "publications__journal",
            "author_affiliations__affiliation",
        )

        publications = (
            Publication.objects.filter(
                authors__in=authors,
            )
            .select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .distinct()
        )

        affiliations = AuthorAffiliation.objects.filter(
            author__in=authors,
        ).select_related(
            "affiliation",
            "publication",
        )

        total_publications = publications.count()

        total_if = sum(p.journal.impact_factor or 0 for p in publications if p.journal)

        avg_if = total_if / total_publications if total_publications else 0

        context.update(
            {
                "first_name": first_name,
                "last_name": last_name,
                "authors": authors,
                "publications": publications,
                "affiliations": affiliations,
                "total_publications": total_publications,
                "total_impact_factor": total_if,
                "average_impact_factor": avg_if,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Authors",
                        "url": reverse("dashboard:authors"),
                    },
                    {
                        "label": f"{first_name} {last_name}",
                    },
                ],
            }
        )

        return context


# =====================================================
# JOURNALS
# =====================================================
class JournalsView(TemplateView):
    template_name = "dashboard/journals.html"

    paginate_by = 10

    search_fields = [
        "journal__name",
        "title",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "date_published",
        "journal__impact_factor",
    ]

    gt_filters = []

    lt_filters = []

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # --------------------------------------------------
        # Publications
        # --------------------------------------------------

        publications = Publication.objects.select_related("journal")

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        # --------------------------------------------------
        # Journal Aggregation
        # --------------------------------------------------

        journals = (
            publications.values(
                "journal__id",
                "journal__name",
                "journal__impact_factor",
            )
            .annotate(
                total_publications=Count(
                    "id",
                    distinct=True,
                ),
                average_impact_factor=Avg(
                    "journal__impact_factor",
                ),
                total_impact_factor=Sum(
                    "journal__impact_factor",
                ),
            )
            .order_by("-total_publications")
        )

        journals_data = list(journals)

        # --------------------------------------------------
        # Pagination
        # --------------------------------------------------

        paginator = Paginator(journals_data, self.paginate_by)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        # --------------------------------------------------
        # Summary Cards
        # --------------------------------------------------

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        # --------------------------------------------------
        # Top Journal
        # --------------------------------------------------

        top_journal = journals_data[0] if journals_data else None

        context.update(
            {
                # Filters
                "filter": filterset,
                # Table
                "page_obj": page_obj,
                # Charts
                "journals_data": journals_data,
                "journal_chart_data": journals_data,
                # KPI Cards
                "journal_count": (page_obj.paginator.count),
                "journal_total_publications": (summary["total_publications"] or 0),
                "journal_total_impact": (summary["total_impact_factor"] or 0),
                "journal_average_impact": (summary["average_impact_factor"] or 0),
                "journal_highest_impact": (summary["highest_impact_factor"] or 0),
                # Top Journal
                "journal_top_name": (
                    top_journal["journal__name"] if top_journal else None
                ),
                "journal_top_count": (
                    top_journal["total_publications"] if top_journal else 0
                ),
                # Header
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Journal Overview",
                    },
                ],
            }
        )

        return context


class JournalDetailView(TemplateView):
    template_name = "dashboard/journal_detail.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        journal = get_object_or_404(
            Journal,
            pk=self.kwargs["journal_id"],
        )

        publications = (
            Publication.objects.filter(journal=journal)
            .select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .order_by("-date_published")
        )

        paginator = Paginator(
            publications,
            self.paginate_by,
        )

        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            first_publication=Min("date_published"),
            latest_publication=Max("date_published"),
        )

        context.update(
            {
                "journal": journal,
                "page_obj": page_obj,
                "total_publications": summary["total_publications"] or 0,
                "total_impact_factor": summary["total_impact_factor"] or 0,
                "average_impact_factor": summary["average_impact_factor"] or 0,
                "first_publication": summary["first_publication"],
                "latest_publication": summary["latest_publication"],
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Journal Overview",
                        "url": reverse("dashboard:journals"),
                    },
                    {
                        "label": journal.name,
                    },
                ],
            }
        )

        return context


# =====================================================
# DEPARTMENTS
# =====================================================
class DepartmentsView(TemplateView):
    template_name = "dashboard/departments.html"

    paginate_by = 10

    search_fields = [
        "departments__name",
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "date_published",
    ]

    gt_filters = []

    lt_filters = []

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # --------------------------------------------------
        # Publications
        # --------------------------------------------------

        publications = Publication.objects.select_related("journal").prefetch_related(
            "departments"
        )

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        # --------------------------------------------------
        # Department Aggregation
        # --------------------------------------------------

        departments = (
            publications.values(
                "departments__id",
                "departments__name",
            )
            .annotate(
                total_publications=Count(
                    "id",
                    distinct=True,
                ),
                average_impact_factor=Avg(
                    "journal__impact_factor",
                ),
                total_impact_factor=Sum(
                    "journal__impact_factor",
                ),
            )
            .order_by("-total_publications")
        )

        departments_data = list(departments)

        # --------------------------------------------------
        # Pagination
        # --------------------------------------------------

        paginator = Paginator(departments_data, self.paginate_by)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        # --------------------------------------------------
        # Summary Cards
        # --------------------------------------------------

        summary = publications.aggregate(
            total_publications=Count(
                "id",
                distinct=True,
            ),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        # --------------------------------------------------
        # Top Department
        # --------------------------------------------------

        top_department = departments_data[0] if departments_data else None

        context.update(
            {
                # Filters
                "filter": filterset,
                # Table
                "page_obj": page_obj,
                # Charts
                "departments_data": departments_data,
                "department_chart_data": departments_data,
                # KPI Cards
                "department_count": (page_obj.paginator.count),
                "department_total_publications": (summary["total_publications"] or 0),
                "department_total_impact": (summary["total_impact_factor"] or 0),
                "department_average_impact": (summary["average_impact_factor"] or 0),
                "department_highest_impact": (summary["highest_impact_factor"] or 0),
                # Top Department
                "department_top_name": (
                    top_department["departments__name"] if top_department else None
                ),
                "department_top_count": (
                    top_department["total_publications"] if top_department else 0
                ),
                # Header
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Department Overview",
                    },
                ],
            }
        )

        return context


class DepartmentDetailView(TemplateView):
    template_name = "dashboard/department_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        department_id = self.kwargs["pk"]

        department = get_object_or_404(
            Department,
            pk=department_id,
        )

        publications = (
            Publication.objects.select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .filter(
                departments=department,
            )
            .distinct()
            .order_by("-date_published")
        )

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        paginator = Paginator(publications, 10)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        context.update(
            {
                "department": department,
                "page_obj": page_obj,
                "publication_count": summary["total_publications"] or 0,
                "total_impact": summary["total_impact_factor"] or 0,
                "average_impact": summary["average_impact_factor"] or 0,
                "highest_impact": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Department Overview",
                        "url": reverse("dashboard:departments"),
                    },
                    {
                        "label": department.name,
                    },
                ],
            }
        )

        return context


# =====================================================
# COLLABORATION OVERVIEW
# =====================================================
class CollaborationView(TemplateView):
    template_name = "dashboard/collaboration.html"

    paginate_by = 10

    search_fields = [
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "date_published",
    ]

    gt_filters = []
    lt_filters = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        publications = Publication.objects.select_related("journal")

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        collaboration_types = (
            publications.values("collaboration_type")
            .annotate(
                total_publications=Count("id"),
                average_impact_factor=Avg("journal__impact_factor"),
                total_impact_factor=Sum("journal__impact_factor"),
            )
            .order_by("-total_publications")
        )

        collaboration_types_data = list(collaboration_types)

        paginator = Paginator(collaboration_types, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        top_type = collaboration_types_data[0] if collaboration_types_data else None

        context.update(
            {
                # Filter
                "filter": filterset,
                # Table
                "page_obj": page_obj,
                # Charts
                "collaboration_types_data": collaboration_types_data,
                # Optional chart alias
                "collaboration_chart_data": collaboration_types_data,
                # KPI Cards
                "collaboration_type_count": page_obj.paginator.count,
                "collaboration_total_publications": summary["total_publications"] or 0,
                "collaboration_total_impact": summary["total_impact_factor"] or 0,
                "collaboration_average_impact": summary["average_impact_factor"] or 0,
                "collaboration_highest_impact": summary["highest_impact_factor"] or 0,
                # Top Collaboration Type
                "collaboration_top_type": (
                    top_type["collaboration_type"] if top_type else None
                ),
                "collaboration_top_count": (
                    top_type["total_publications"] if top_type else 0
                ),
                # Header
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Collaboration Overview",
                    },
                ],
            }
        )

        return context


class CollaborationDetailView(TemplateView):
    template_name = "dashboard/collaboration_detail.html"

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        collaboration_type = self.kwargs["collaboration_type"]

        publications = (
            Publication.objects.filter(collaboration_type=collaboration_type)
            .select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .order_by("-date_published")
        )

        paginator = Paginator(
            publications,
            self.paginate_by,
        )

        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "collaboration_type": collaboration_type,
                "page_obj": page_obj,
                "publication_count": summary["total_publications"] or 0,
                "total_impact_factor": summary["total_impact_factor"] or 0,
                "average_impact_factor": summary["average_impact_factor"] or 0,
                "highest_impact_factor": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Collaboration Overview",
                        "url": reverse("dashboard:collaboration"),
                    },
                    {
                        "label": collaboration_type,
                    },
                ],
            }
        )

        return context


# =====================================================
# COUNTRY COLLABORATION
# =====================================================
class CountryCollaborationView(TemplateView):
    template_name = "dashboard/country_collaboration.html"

    paginate_by = 10

    search_fields = [
        "author_affiliations__affiliation__country",
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "publications",
    ]

    gt_filters = []
    lt_filters = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        publications = Publication.objects.select_related("journal").prefetch_related(
            "author_affiliations__affiliation"
        )

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        countries = (
            publications.values("author_affiliations__affiliation__country")
            .exclude(author_affiliations__affiliation__country__isnull=True)
            .exclude(author_affiliations__affiliation__country="")
            .annotate(
                publications=Count("id", distinct=True),
                total_impact_factor=Sum("journal__impact_factor"),
                average_impact_factor=Avg("journal__impact_factor"),
            )
        )

        merged = {}

        for row in countries:
            country = (row["author_affiliations__affiliation__country"] or "").strip()

            # Remove trailing semicolons
            country = country.rstrip(";").strip()

            if country not in merged:
                merged[country] = {
                    "author_affiliations__affiliation__country": country,
                    "publications": 0,
                    "total_impact_factor": 0,
                }

            merged[country]["publications"] += row["publications"] or 0
            merged[country]["total_impact_factor"] += row["total_impact_factor"] or 0

        for row in merged.values():
            if row["publications"]:
                row["average_impact_factor"] = (
                    row["total_impact_factor"] / row["publications"]
                )
            else:
                row["average_impact_factor"] = 0

        countries_data = sorted(
            merged.values(),
            key=lambda x: x["publications"],
            reverse=True,
        )
        chart_data = countries_data[:10]

        paginator = Paginator(countries_data, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        top_country = countries_data[0] if countries_data else None

        context.update(
            {
                "filter": filterset,
                "page_obj": page_obj,
                "countries_data": countries_data,
                "country_chart_data": chart_data,
                "country_count": page_obj.paginator.count,
                "country_total_publications": summary["total_publications"] or 0,
                "country_total_impact": summary["total_impact_factor"] or 0,
                "country_average_impact": summary["average_impact_factor"] or 0,
                "country_highest_impact": summary["highest_impact_factor"] or 0,
                "country_top": (
                    top_country["author_affiliations__affiliation__country"]
                    if top_country
                    else None
                ),
                "country_top_count": (
                    top_country["publications"] if top_country else 0
                ),
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Country Collaboration",
                    },
                ],
            }
        )

        return context


class CountryCollaborationDetailView(TemplateView):
    template_name = "dashboard/country_collaboration_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        country = unquote(kwargs["country"]).rstrip(";").strip()

        publications = (
            Publication.objects.select_related("journal")
            .prefetch_related(
                "authors",
                Prefetch(
                    "author_affiliations",
                    queryset=AuthorAffiliation.objects.select_related(
                        "author",
                        "affiliation",
                    ),
                ),
            )
            .filter(author_affiliations__affiliation__country__iregex=rf"^{country};?$")
            .distinct()
            .order_by("-date_published")
        )

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "country": country,
                "publications": publications,
                "publication_count": summary["total_publications"] or 0,
                "total_impact": summary["total_impact_factor"] or 0,
                "average_impact": summary["average_impact_factor"] or 0,
                "highest_impact": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Country Collaboration",
                        "url": reverse("dashboard:country_collaboration"),
                    },
                    {
                        "label": country,
                    },
                ],
            }
        )

        return context


# =====================================================
# INSTITUTION COLLABORATION
# =====================================================
class InstitutionCollaborationView(TemplateView):
    template_name = "dashboard/institution_collaboration.html"

    paginate_by = 10

    search_fields = [
        "author_affiliations__affiliation__name",
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "publications",
    ]

    gt_filters = []
    lt_filters = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        publications = Publication.objects.select_related("journal").prefetch_related(
            "author_affiliations__affiliation"
        )

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        institutions = (
            publications.values("author_affiliations__affiliation__name")
            .exclude(author_affiliations__affiliation__name__isnull=True)
            .exclude(author_affiliations__affiliation__name="")
            .annotate(
                publications=Count("id", distinct=True),
                total_impact_factor=Sum("journal__impact_factor"),
                average_impact_factor=Avg("journal__impact_factor"),
            )
        )

        merged = {}

        for row in institutions:
            name = (row["author_affiliations__affiliation__name"] or "").strip()

            if name not in merged:
                merged[name] = {
                    "author_affiliations__affiliation__name": name,
                    "publications": 0,
                    "total_impact_factor": 0,
                }

            merged[name]["publications"] += row["publications"] or 0
            merged[name]["total_impact_factor"] += row["total_impact_factor"] or 0

        for row in merged.values():
            row["average_impact_factor"] = (
                row["total_impact_factor"] / row["publications"]
                if row["publications"]
                else 0
            )

        institutions_data = sorted(
            merged.values(),
            key=lambda x: x["publications"],
            reverse=True,
        )

        institution_chart_data = institutions_data[:10]

        paginator = Paginator(institutions_data, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        top_institution = institutions_data[0] if institutions_data else None

        context.update(
            {
                "filter": filterset,
                "page_obj": page_obj,
                "institutions_data": institutions_data,
                "institution_chart_data": institution_chart_data,
                "institution_count": page_obj.paginator.count,
                "institution_total_publications": summary["total_publications"] or 0,
                "institution_total_impact": summary["total_impact_factor"] or 0,
                "institution_average_impact": summary["average_impact_factor"] or 0,
                "institution_highest_impact": summary["highest_impact_factor"] or 0,
                "institution_top": (
                    top_institution["author_affiliations__affiliation__name"]
                    if top_institution
                    else None
                ),
                "institution_top_count": (
                    top_institution["publications"] if top_institution else 0
                ),
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Institution Collaboration",
                    },
                ],
            }
        )

        return context


class InstitutionCollaborationDetailView(TemplateView):
    template_name = "dashboard/institution_collaboration_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        institution = unquote(kwargs["institution"]).strip()

        publications = (
            Publication.objects.select_related("journal")
            .prefetch_related(
                "authors",
                Prefetch(
                    "author_affiliations",
                    queryset=AuthorAffiliation.objects.select_related(
                        "author",
                        "affiliation",
                    ),
                ),
            )
            .filter(author_affiliations__affiliation__name=institution)
            .distinct()
            .order_by("-date_published")
        )

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "institution": institution,
                "publications": publications,
                "publication_count": summary["total_publications"] or 0,
                "total_impact": summary["total_impact_factor"] or 0,
                "average_impact": summary["average_impact_factor"] or 0,
                "highest_impact": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Institution Collaboration",
                        "url": reverse("dashboard:institution_collaboration"),
                    },
                    {
                        "label": institution,
                    },
                ],
            }
        )

        return context


# =====================================================
# PUBLICATION TRENDS
# =====================================================
class TrendsView(TemplateView):
    template_name = "dashboard/trends.html"

    search_fields = [
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "date_published",
    ]

    gt_filters = []
    lt_filters = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = Publication.objects.select_related("journal")

        filterset = DynamicFilter(
            self.request.GET,
            queryset=queryset,
            view=self,
        )

        filtered = filterset.qs

        publication_trends = (
            filtered.values("date_published__year")
            .annotate(
                total=Count("id"),
                avg_if=Avg("journal__impact_factor"),
                total_impact_factor=Sum("journal__impact_factor"),
            )
            .order_by("date_published__year")
        )

        publication_trends_data = list(publication_trends)

        paginator = Paginator(publication_trends, 10)

        page_number = self.request.GET.get("page")

        page_obj = paginator.get_page(page_number)

        totals = filtered.aggregate(
            total_publications=Count("id"),
            total_impact=Sum("journal__impact_factor"),
        )

        latest_year = (
            publication_trends_data[-1]["date_published__year"]
            if publication_trends_data
            else None
        )

        yoy_change = None

        if len(publication_trends_data) >= 2:
            previous = publication_trends_data[-2]["total"]
            current = publication_trends_data[-1]["total"]

            if previous:
                yoy_change = ((current - previous) / previous) * 100

        context.update(
            {
                "filter": filterset,
                "page_obj": page_obj,
                "publication_trends": page_obj,
                "publication_trends_data": publication_trends_data,
                "trend_years_tracked": len(publication_trends_data),
                "trend_total_publications": totals["total_publications"] or 0,
                "trend_total_impact": totals["total_impact"] or 0,
                "trend_latest_year": latest_year,
                "trend_yoy_change": yoy_change,
            }
        )

        return context


class TrendYearDetailView(TemplateView):
    template_name = "dashboard/trend_year_detail.html"

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = self.kwargs["year"]

        publications = (
            Publication.objects.filter(date_published__year=year)
            .select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .order_by("-date_published")
        )

        paginator = Paginator(
            publications,
            self.paginate_by,
        )

        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "year": year,
                "page_obj": page_obj,
                "publication_count": summary["total_publications"] or 0,
                "total_impact": summary["total_impact_factor"] or 0,
                "average_impact": summary["average_impact_factor"] or 0,
                "highest_impact": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Publication Trends",
                        "url": reverse("dashboard:trends"),
                    },
                    {
                        "label": str(year),
                    },
                ],
            }
        )

        return context


# =====================================================
# IMPACT ANALYSIS
# =====================================================
class ImpactView(TemplateView):
    template_name = "dashboard/impact.html"

    # Used by DynamicFilter
    search_fields = [
        "journal__name",
        "title",
        "doi",
    ]

    sortable_columns = [
        "date_published",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = Publication.objects.select_related("journal")

        filterset = DynamicFilter(
            self.request.GET,
            queryset=queryset,
            view=self,
        )

        filtered = filterset.qs

        journal_impact = (
            filtered.values(
                "journal__id",
                "journal__name",
            )
            .annotate(
                total_publications=Count("id"),
                average_impact_factor=Avg("journal__impact_factor"),
                total_impact_factor=Sum("journal__impact_factor"),
            )
            .order_by("-average_impact_factor")
        )

        journal_impact_data = list(journal_impact)

        paginator = Paginator(journal_impact_data, 10)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = filtered.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "filter": filterset,
                "page_obj": page_obj,
                # Full data (for charts)
                "journal_impact_data": journal_impact_data,
                # KPIs
                "impact_total_journals": len(journal_impact_data),
                "impact_total_publications": summary["total_publications"] or 0,
                "impact_total_factor": summary["total_impact_factor"] or 0,
                "impact_average_factor": summary["average_impact_factor"] or 0,
                "impact_highest_factor": summary["highest_impact_factor"] or 0,
            }
        )

        return context


class ImpactDetailView(TemplateView):
    template_name = "dashboard/impact_detail.html"

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        journal = get_object_or_404(
            Journal,
            pk=self.kwargs["journal_id"],
        )

        publications = (
            Publication.objects.filter(
                journal=journal,
            )
            .select_related("journal")
            .prefetch_related(
                "authors",
                "departments",
            )
            .order_by("-date_published")
        )

        paginator = Paginator(
            publications,
            self.paginate_by,
        )

        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            total_publications=Count("id"),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        context.update(
            {
                "journal": journal,
                "page_obj": page_obj,
                "total_publications": summary["total_publications"] or 0,
                "total_impact_factor": summary["total_impact_factor"] or 0,
                "average_impact_factor": summary["average_impact_factor"] or 0,
                "highest_impact_factor": summary["highest_impact_factor"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "Impact Analysis",
                        "url": reverse("dashboard:impact"),
                    },
                    {
                        "label": journal.name,
                    },
                ],
            }
        )

        return context


# =====================================================
# RRI ROLE
# =====================================================
class RRIRoleView(TemplateView):
    template_name = "dashboard/rri_role.html"

    paginate_by = 10

    search_fields = [
        "authors__first_name",
        "authors__last_name",
        "authors__rri_role",
        "title",
        "journal__name",
        "doi",
    ]

    exact_filters = [
        "document_type",
        "collaboration_type",
    ]

    date_filters = [
        "date_published",
    ]

    sortable_columns = [
        "date_published",
    ]

    gt_filters = []

    lt_filters = []

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # --------------------------------------------------
        # Publications
        # --------------------------------------------------

        publications = Publication.objects.select_related("journal").prefetch_related(
            "authors"
        )

        # --------------------------------------------------
        # Filters
        # --------------------------------------------------

        filterset = DynamicFilter(
            self.request.GET,
            queryset=publications,
            view=self,
        )

        publications = filterset.qs

        # --------------------------------------------------
        # RRI Role Aggregation
        # --------------------------------------------------

        roles = (
            publications.values(
                "authors__rri_role",
            )
            .annotate(
                total_publications=Count(
                    "id",
                    distinct=True,
                ),
                average_impact_factor=Avg(
                    "journal__impact_factor",
                ),
                total_impact_factor=Sum(
                    "journal__impact_factor",
                ),
            )
            .order_by("-total_publications")
        )

        roles_data = list(roles)

        # --------------------------------------------------
        # Pagination
        # --------------------------------------------------

        paginator = Paginator(roles_data, self.paginate_by)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        # --------------------------------------------------
        # Summary Cards
        # --------------------------------------------------

        summary = publications.aggregate(
            total_publications=Count(
                "id",
                distinct=True,
            ),
            total_impact_factor=Sum("journal__impact_factor"),
            average_impact_factor=Avg("journal__impact_factor"),
            highest_impact_factor=Max("journal__impact_factor"),
        )

        # --------------------------------------------------
        # Top Role
        # --------------------------------------------------

        top_role = roles_data[0] if roles_data else None

        context.update(
            {
                # Filter
                "filter": filterset,
                # Table
                "page_obj": page_obj,
                # Charts
                "rri_roles_data": roles_data,
                "rri_role_chart_data": roles_data,
                # KPI
                "rri_role_count": (page_obj.paginator.count),
                "rri_role_total_publications": (summary["total_publications"] or 0),
                "rri_role_total_impact": (summary["total_impact_factor"] or 0),
                "rri_role_average_impact": (summary["average_impact_factor"] or 0),
                "rri_role_highest_impact": (summary["highest_impact_factor"] or 0),
                # Top Role
                "rri_role_top_name": (
                    top_role["authors__rri_role"] if top_role else None
                ),
                "rri_role_top_count": (
                    top_role["total_publications"] if top_role else 0
                ),
                # Breadcrumb
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "RRI Role Overview",
                    },
                ],
            }
        )

        return context


class RRIRoleDetailView(TemplateView):
    template_name = "dashboard/rri_role_detail.html"

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        role = self.kwargs["role"]

        publications = (
            Publication.objects.filter(authors__rri_role=role)
            .select_related("journal")
            .prefetch_related("authors", "departments")
            .distinct()
            .order_by("-date_published")
        )

        paginator = Paginator(publications, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        summary = publications.aggregate(
            publication_count=Count("id", distinct=True),
            total_impact=Sum("journal__impact_factor"),
            average_impact=Avg("journal__impact_factor"),
            highest_impact=Max("journal__impact_factor"),
        )

        authors = (
            Author.objects.filter(rri_role=role)
            .distinct()
            .order_by("first_name", "last_name")
        )

        context.update(
            {
                "role": role,
                "page_obj": page_obj,
                "publications": page_obj,
                "authors": authors,
                "publication_count": summary["publication_count"] or 0,
                "total_impact": summary["total_impact"] or 0,
                "average_impact": summary["average_impact"] or 0,
                "highest_impact": summary["highest_impact"] or 0,
                "breadcrumbs": [
                    {
                        "label": "Dashboard",
                        "url": reverse("dashboard:home"),
                    },
                    {
                        "label": "RRI Roles",
                        "url": reverse("dashboard:rri_role"),
                    },
                    {
                        "label": role,
                    },
                ],
            }
        )

        return context
