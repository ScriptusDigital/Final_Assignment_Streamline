""" Rest API views for the assets app. """

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Collection, Tag
from .permissions import TaxonomyPermission
from .serializers import CollectionSerializer, TagSerializer

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