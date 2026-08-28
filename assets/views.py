""" Rest API views for the assets app. """

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Asset, Collection, Tag
from .permissions import AssetPermission, TaxonomyPermission
from .serializers import (AssetSerializer,CollectionSerializer,TagSerializer,
)
from .services import workflow_service


class AssetPagination(PageNumberPagination):
    """ Custom pagination class for Asset model. """
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100

def visible_assets_for_user(user):
    """ Return a queryset of assets visible to the given user. """
    queryset = Asset.objects.select_related("uploader", "approver").prefetch_related("tags", "collections", "collections_created_by")

    role = workflow_service.user_role(user)
    if role == "admin":
        return queryset

    today = timezone.now().date()

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
    """ ViewSet for managing assets. """
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated, AssetPermission]
    pagination_class = AssetPagination

    def get_queryset(self):
        """ Return assets visible to the requesting user. """
        return visible_assets_for_user(self.request.user)


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