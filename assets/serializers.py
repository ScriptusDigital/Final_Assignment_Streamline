from rest_framework import serializers
from .models import Tag
from django.contrib.auth import get_user_model
from rest_framework import serializers
from.models import Collection, Tag
from .serializers import CollectionSerializer, TagSerializer
from rest_framework.test import APIRequestFactory

class UserSummarySerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
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


class CollectionSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)
    asset_count = serializers.IntegerField(read_only=True)  

    class Meta:
            model = Collection
            fields = ("id", "name","slug", "description","created_by","asset_count","created_at",)
            read_only_fields = ("slug", "created_by", "created_at",)

    def create(self, validated_data):
            request = self.context.get('request')

            creator = (request.user if request and request.user.is_authenticated else None)

            return Collection.objects.create(created_by=creator, **validated_data)