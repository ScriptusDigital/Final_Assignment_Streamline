"""Structured metadata filters for the Asset model."""
import django_filters
from .models import Asset

class AssetFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(method='filter_by_tag')

    collection = django_filters.CharFilter(method='filter_by_collection')

    uploaded_by = django_filters.CharFilter(method='filter_by_uploaded_by')

    expiry_before = django_filters.DateFilter(
        field_name="expiry_date",
        lookup_expr="lte",
    )
    created_after = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )
    has_expiry = django_filters.BooleanFilter(
        field_name="expiry_date",
        lookup_expr="isnull",
        exclude=True,
    )

    class Meta:
        model = Asset
        fields = ('status', 'rights_status', 'permitted_use',)

    def filter_by_tag(
        self,
        queryset,
        name,
        value,
    ):
        lookup = (
            {"tags__id": value}
            if str(value).isdigit()
            else {"tags__slug": value}
        )

        return queryset.filter(**lookup)

    def filter_collection(
        self,
        queryset,
        name,
        value,
    ):
        lookup = (
            {"collections__id": value}
            if str(value).isdigit()
            else {"collections__slug": value}
        )

        return queryset.filter(**lookup)