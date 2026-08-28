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