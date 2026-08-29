"""Structured metadata filters for the Asset model."""
import django_filters
from .models import Asset

class AssetFilter(django_filters.FilterSet):
    class Meta:
        model = Asset
        fields = {
            'name': ['icontains'],
            'description': ['icontains'],
            'created_at': ['exact', 'year__gt', 'year__lt'],
        }