from rest_framework import serializers
from .models import Tag
from django.contrib.auth import get_user_model
from.models import Asset, Collection, Tag, AssetEvent
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

class UserSummarySerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'display_name', 'role')
    def get_display_name(self, obj):
        return obj.get_full_name().strip() or obj.email

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


class AssetEventSerializer(serializers.ModelSerializer):
    actor = UserSummarySerializer(read_only=True)
    action_label = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AssetEvent
        fields = ("id","actor","action","action_label","from_status","to_status","message","metadata","created_at",
        )


class AssetSerializer(serializers.ModelSerializer):
    """ JSON representation of an Asset, including the creator, collection, and tags. """
    
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source="tags",
        write_only=True,
        required=False,
    )
    collections = CollectionSerializer(read_only=True, many=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Collection.objects.all(),
        source="collections",
        write_only=True,
        required=False,
    )
    uploader = UserSummarySerializer(read_only=True)
    approver = UserSummarySerializer(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_viewer_accessible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Asset
        fields = (
            "id",
            "title",
            "caption",
            "alt_text",
            "photographer_credit",
            "event_name",
            "location",
            "captured_at",
            "notes",
            "tags",
            "tag_ids",
            "collections",
            "collection_ids",
            "rights_status",
            "permitted_use",
            "licence_details",
            "expiry_date",
            "status",
            "uploader",
            "approver",
            "approved_at",
            "archived_at",
            "cloudinary_asset_id",
            "public_id",
            "delivery_type",
            "secure_url",
            "original_filename",
            "image_format",
            "width",
            "height",
            "bytes",
            "version",
            "created_at",
            "updated_at",
            "is_expired",
            "is_viewer_accessible",
        )

        read_only_fields = (
             "status",
            "uploader",
            "approver",
            "approved_at",
            "archived_at",
            "cloudinary_asset_id",
            "public_id",
            "delivery_type",
            "secure_url",
            "original_filename",
            "image_format",
            "width",
            "height",
            "bytes",
            "version",
            "created_at",
            "updated_at",
        )

        tag_ids = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Tag.objects.all(),
            source='tags',
            write_only=True,
            required=False,
        )

        collection_ids = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Collection.objects.all(),
            source='collections',
            write_only=True,
            required=False,
        )

    def update(self, instance, validated_data):
        tags_marker = object()
        collections_marker = object()

        tags = validated_data.pop("tags", tags_marker)
        collections = validated_data.pop(
            "collections",
            collections_marker,
        )

        changed_fields = list(validated_data)

        if tags is not tags_marker:
            changed_fields.append("tags")

        if collections is not collections_marker:
            changed_fields.append("collections")

        try:
            with transaction.atomic():
                for field, value in validated_data.items():
                    setattr(instance, field, value)

                instance.full_clean()
                instance.save()

                if tags is not tags_marker:
                    instance.tags.set(tags)

                if collections is not collections_marker:
                    instance.collections.set(collections)

                if changed_fields:
                    AssetEvent.objects.create(
                        asset=instance,
                        actor=self.context["request"].user,
                        action=AssetEvent.Action.UPDATED,
                        from_status=instance.status,
                        to_status=instance.status,
                        metadata={
                            "changed_fields": changed_fields,
                        },
                    )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
            ) from exc

        return instance