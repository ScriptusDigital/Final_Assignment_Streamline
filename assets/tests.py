""" Tests for asset models """


from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Asset, Tag


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