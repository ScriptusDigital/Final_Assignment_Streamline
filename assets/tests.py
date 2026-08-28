""" Tests for asset models """

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Asset, Tag
from django.db.models import Count
from .serializers import CollectionSerializer, TagSerializer
from rest_framework.test import APIRequestFactory


def cloudinary_response(number=1):
    """Dummy provider data without contacting Cloudinary."""

    return {
        "cloudinary_asset_id": f"immutable-{number}",
        "public_id": f"streamline/assets/public-{number}",
        "delivery_type": "authenticated",
        "secure_url": (
            "https://res.cloudinary.com/demo/"
            f"image/authenticated/v1/public-{number}"
        ),
        "original_filename": f"photo-{number}",
        "image_format": "png",
        "width": 1200,
        "height": 800,
        "bytes": 23456,
        "version": number,
    }

class AssetFactoryMixin:
    asset_number = 0

    def make_asset(self, uploader, **overrides):
        type(self).asset_number += 1
        number = type(self).asset_number

        values = {
            "uploader": uploader,
            "title": f"Finish line {number}",
            "caption": (
                "Runner crossing the city marathon "
                "finish line"
            ),
            "alt_text": (
                "A runner crosses the finish line"
            ),
            "photographer_credit": "Alex Example",
            "event_name": "City Marathon",
            "rights_status": (
                Asset.RightsStatus.CLEARED
            ),
            "permitted_use": (
                Asset.PermittedUse.EDITORIAL
            ),
            **cloudinary_response(number),
        }

        values.update(overrides)

        return Asset.objects.create(**values)

class AssetModelTests(AssetFactoryMixin, TestCase):
    def setUp(self):
        User = get_user_model()

        self.editor = User.objects.create_user(
            email="editor-model@example.com",
            password="test-password",
            role="editor",
        )
        self.admin = User.objects.create_user(
            email="admin-model@example.com",
            password="test-password",
            role="admin",
        )

    def test_asset_uses_uuid_and_cloudinary_identifiers(self):
        asset = self.make_asset(uploader=self.editor)

        self.assertEqual(asset.id.version, 4)
        self.assertTrue(asset.cloudinary_asset_id.startswith("immutable-"
            )
        )
        self.assertTrue(asset.public_id.startswith("streamline/assets/"
            )
        )

    def test_viewer_access_requires_unexpired_rights(self):
        asset = self.make_asset(
            self.editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
            expiry_date=(
                timezone.localdate()
                + timedelta(days=1)
            ),
        )

        self.assertTrue(asset.is_viewer_accessible)

        asset.expiry_date = (
            timezone.localdate()
            - timedelta(days=1)
        )

        self.assertTrue(asset.is_expired)
        self.assertFalse(asset.is_viewer_accessible)

    def test_approved_asset_rejects_unknown_rights(self):
        asset = self.make_asset(
            self.editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
            rights_status=Asset.RightsStatus.UNKNOWN,
        )

        with self.assertRaises(ValidationError):
            asset.full_clean()

    def test_tag_slug_is_generated_and_unique(self):
        first = Tag.objects.create(
            name="Press Area"
        )
        second = Tag.objects.create(
            name="Press-Area"
        )

        self.assertEqual(
            first.slug,
            "press-area",
        )
        self.assertEqual(
            second.slug,
            "press-area-2",
        )


class TagSerializerTests(TestCase):
    def test_serializer_returns_slug_and_asset_count(self):
        tag = Tag.objects.create(name="Athletics")

        tag = Tag.objects.annotate(asset_count=Count('assets')).get(pk=tag.pk)
        data = TagSerializer(tag).data


        self.assertEqual(data['name'], 'Athletics')
        self.assertEqual(data['slug'], 'athletics')
        self.assertEqual(data['asset_count'], 0)

    def test_slug_and_asset_count_are_read_only(self):
        serializer = TagSerializer(data={
            "name": "Press Area",
            "slug": "manually-forced",
            "asset_count": 99,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

        tag = serializer.save()

        self.assertEqual(tag.slug, "press-area")
        self.assertFalse(hasattr(tag, "asset_count"))

class CollectionSerializerTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.editor = User.objects.create_user(
            email="collection.editor@example.com",
            password="test-password",
            first_name="Rich",  
            last_name="Editor",
            role=User.Role.EDITOR,
        )

        self.request = APIRequestFactory().post("/api/collections/")
        self.request.user = self.editor

    def test_create_assigns_authenticated_user(self):
            serializer = CollectionSerializer(
                data={
                    "name": "Paris Games",
                    "description": "Photography from the Paris event.",
                },
                context={"request": self.request},
            )

            self.assertTrue(serializer.is_valid(), serializer.errors)

            collection = serializer.save()

            self.assertEqual(collection.created_by, self.editor)
            self.assertEqual(collection.slug, "paris-games")
