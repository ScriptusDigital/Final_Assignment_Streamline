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
         "public_id": f"test_image_{number}",
         "version": 1234567890,
         "signature": "dummy_signature",
         "width": 800,
         "height": 600,
         "format": "jpg",
         "resource_type": "image",
         "created_at": timezone.now().isoformat(),
         "tags": [],
         "bytes": 123456,
         "type": "upload",
         "etag": "dummy_etag",
         "placeholder": False,
         "url": f"http://res.cloudinary.com/demo/image/upload/v1234567890/test_image_{number}.jpg",
         "secure_url": f"https://res.cloudinary.com/demo/image/upload/v1234567890/test_image_{number}.jpg",
     }