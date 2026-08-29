""" Rest API views for the assets app. """

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Asset, Collection, Tag
from .permissions import AssetPermission, TaxonomyPermission
from .serializers import (AssetSerializer,CollectionSerializer,TagSerializer, DashboardSerializer
)
from .services import workflow_service
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import (DjangoFilterBackend,)
from rest_framework.filters import OrderingFilter
from .filters import AssetFilter

from django.contrib.postgres.search import (SearchVector, SearchQuery, SearchRank)
from django.db import connection

class AssetPagination(PageNumberPagination):
    """ Custom pagination class for Asset model. """
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100

def visible_assets_for(user):
    """Return only assets that the user is permitted to discover."""

    queryset = (
        Asset.objects
        .select_related("uploader", "approver")
        .prefetch_related(
            "tags",
            "collections",
            "collections__created_by",
        )
    )

    role = workflow_service.user_role(user)

    if role == "admin":
        return queryset

    today = timezone.localdate()

    viewer_rule = (
        Q(
            status=Asset.Status.APPROVED,
            rights_status__in=(
                Asset.RightsStatus.CLEARED,
                Asset.RightsStatus.RESTRICTED,
            ),
        )
        & ~Q(
            permitted_use=Asset.PermittedUse.INTERNAL
        )
        & (
            Q(expiry_date__isnull=True)
            | Q(expiry_date__gte=today)
        )
    )

    if role == "editor":
        return queryset.filter(
            Q(uploader=user) | viewer_rule
        ).distinct()

    if role == "viewer":
        return queryset.filter(viewer_rule).distinct()

    return queryset.none()

class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = (
        IsAuthenticated,
        AssetPermission,
    )
    pagination_class = AssetPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_class = AssetFilter

    ordering_fields = (
        "created_at",
        "updated_at",
        "captured_at",
        "title",
        "expiry_date",
    )
 

    http_method_names = ["get", "post", "head", "patch", "options"]

    def get_queryset(self):
        """Return viewable assets for the current user, with related fields preloaded."""
        queryset = visible_assets_for(
        self.request.user
    )

        query = self.request.query_params.get(
            "q",
            "",
        ).strip()

        if not query:
            return queryset

        if connection.vendor == "postgresql":
            vector = (
                SearchVector(
                    "title",
                    weight="A",
                    config="english",
                )
                + SearchVector(
                    "caption",
                    weight="B",
                    config="english",
                )
                + SearchVector(
                    "alt_text",
                    weight="B",
                    config="english",
                )
                + SearchVector(
                    "event_name",
                    weight="B",
                    config="english",
                )
                + SearchVector(
                    "tags__name",
                    weight="B",
                    config="english",
                )
                + SearchVector(
                    "collections__name",
                    weight="B",
                    config="english",
                )
                + SearchVector(
                    "location",
                    weight="C",
                    config="english",
                )
                + SearchVector(
                    "photographer_credit",
                    weight="C",
                    config="english",
                )
                + SearchVector(
                    "notes",
                    weight="D",
                    config="english",
                )
            )

            search_query = SearchQuery(
                query,
                search_type="websearch",
                config="english",
            )

            return (
                queryset
                .annotate(
                    search_rank=SearchRank(
                        vector,
                        search_query,
                    )
                )
                .filter(search_rank__gt=0)
                .order_by(
                    "-search_rank",
                    "-created_at",
                )
                .distinct()
            )

        return queryset.filter(
            Q(title__icontains=query)
            | Q(caption__icontains=query)
            | Q(alt_text__icontains=query)
            | Q(event_name__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(collections__name__icontains=query)
            | Q(location__icontains=query)
            | Q(
                photographer_credit__icontains=query
            )
            | Q(notes__icontains=query)
        ).distinct()

class DashboardView(APIView):
    """ API view for the dashboard, providing counts of assets by status. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ Return a JSON response with counts of assets by status. """
        queryset = visible_assets_for(request.user)
        today = timezone.localdate()
        thirty_days = today + timedelta(days=30)

        pending_review = queryset.filter(
            status=Asset.Status.IN_REVIEW,
        )

        missing_metadata = queryset.filter(
            Q(alt_text="")
            | Q(photographer_credit="")
            | Q(
                rights_status=(
                    Asset.RightsStatus.UNKNOWN
                )
            )
        ).distinct()

        expiring_rights = (queryset.filter(
                expiry_date__range=(
                    today,
                    thirty_days,
                )
            )
            .exclude(
                rights_status=(
                    Asset.RightsStatus.EXPIRED
                )
            )
        )

        status_breakdown = {
            value: 0
            for value, _label in Asset.Status.choices
        }

        status_counts = (
            queryset
            .values("status")
            .annotate(count=Count("id"))
        )

        for item in status_counts:
            status_breakdown[item["status"]] = item["count"]


        dashboard_data = {"total_assets": queryset.count(),
            "status_breakdown": status_breakdown,
            "pending_review_count": (
                pending_review.count()
            ),
            "missing_metadata_count": (
                missing_metadata.count()
            ),
            "expiring_rights_count": (
                expiring_rights.count()
            ),
            "pending_review": pending_review[:6],
            "expiring_rights": (
                expiring_rights
                .order_by("expiry_date")[:6]
            ),
            "recent_assets": queryset[:6],
        }

        serializer = DashboardSerializer(dashboard_data, context={"request": request})
        return Response(serializer.data)





class TagViewSet(viewsets.ModelViewSet):
    """ ViewSet for managing tags. """
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, TaxonomyPermission]

    pagination_class = None  

    def get_queryset(self):
        """ Return all tags with the count of associated assets. """
        return Tag.objects.annotate(asset_count=Count("assets", distinct=True)).order_by("name")

class CollectionViewSet(viewsets.ModelViewSet):
    """ ViewSet for managing collections. """
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated, TaxonomyPermission]
    pagination_class = None

    def get_queryset(self):
        """ Return all collections with the count of associated assets. """
        return Collection.objects.select_related("created_by").annotate(asset_count=Count("assets",distinct=True)).order_by("name")