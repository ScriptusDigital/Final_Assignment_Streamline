from rest_framework import serializers
from .models import Tag

from django.contrib.auth import get_user_model
from rest_framework import serializers

from.models import Collection, Tag

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'display_name', 'role')
    def get_display_name(self, obj):
        return obj.get_display_name() or obj.email  

class TagSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'asset_count', 'created_at')
    

        read_only_fields = ('slug', 'created_at')