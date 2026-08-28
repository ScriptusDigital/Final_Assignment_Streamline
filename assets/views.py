""" Rest API views for the assets app. """

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Collection, Tag
from .permissions import TaxonomyPermission
from .serializers import CollectionSerializer, TagSerializer

