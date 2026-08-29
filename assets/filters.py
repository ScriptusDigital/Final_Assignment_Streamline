"""Structured metadata filters for the Asset model."""
import django_filters
from .models import Asset

class AssetFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(method='filter_by_tag')

    collection = django_filters.CharFilter(method='filter_by_collection')

    uploaded_by = django_filters.CharFilter(method='filter_by_uploaded_by')