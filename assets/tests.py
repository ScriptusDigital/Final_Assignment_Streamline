""" Tests for asset models """

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse 

from .models import Asset, AssetEvent, Collection, Tag
from django.db.models import Count
from .serializers import AssetEventSerializer, AssetSerializer, CollectionSerializer, TagSerializer
from rest_framework.test import APIRequestFactory, APITestCase
from django.contrib.auth.models import AnonymousUser
from .services import workflow_service, cloudinary_service

from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from unittest.mock import patch, 

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

def image_upload(
    name="test.png",
    image_format="PNG",
):
    """Create in-memory image for tests."""

    stream = BytesIO()

    Image.new(
        "RGB",
        (16, 12),
        color=(35, 90, 140),
    ).save(
        stream,
        format=image_format,
    )

    return SimpleUploadedFile(
        name,
        stream.getvalue(),
        content_type=(
            f"image/{image_format.lower()}"
        ),
    )
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

    def test_representation_includes_creator_and_asset_count(self):
            collection = Collection.objects.create(
                name="Athletics",
                created_by=self.editor,
            )

            collection = (Collection.objects
            .select_related('created_by')
            .annotate(asset_count=Count('assets'))
            .get(pk=collection.pk)
        )

            data = CollectionSerializer(collection).data

            self.assertEqual(data["created_by"]["email"], self.editor.email)
            self.assertEqual(data["created_by"]["display_name"], "Rich Editor")
            self.assertEqual(data["created_by"]["role"], self.editor.role)
            self.assertEqual(data["asset_count"], 0)


class AssetEventSerializerTests(AssetFactoryMixin, TestCase):
    def setUp(self):
        User = get_user_model()

        self.editor = User.objects.create_user(
            email="event.editor@example.com",
            password="test-password",
            first_name="Alex",
            last_name="Editor",
            role=User.Role.EDITOR,
        )

    def test_event_representation_includes_actor_and_action_label(self):
        asset = self.make_asset(self.editor)

        event = AssetEvent.objects.create(
            asset=asset,
            actor=self.editor,
            action=AssetEvent.Action.SUBMITTED,
            from_status=Asset.Status.DRAFT,
            to_status=Asset.Status.IN_REVIEW,
            message="Ready for review.",
        )
        data = AssetEventSerializer(event).data

        self.assertEqual(data["actor"]["email"], self.editor.email)
        self.assertEqual(data["actor"]["display_name"], "Alex Editor")
        self.assertEqual(data["action"], "submitted")
        self.assertEqual(data["action_label"],"Submitted for review",)
        self.assertEqual(data["to_status"], "in_review")
        self.assertEqual(data["message"], "Ready for review.")
        self.assertEqual(data["metadata"], {})

class AssetSerializerTests(AssetFactoryMixin, TestCase):
    def setUp(self):
        User = get_user_model()

        self.editor = User.objects.create_user(
            email="asset.editor@example.com",
            password="test-password",
            first_name="Sam",
            last_name="Editor",
            role=User.Role.EDITOR,
        )

        self.admin = User.objects.create_user(
            email="asset.admin@example.com",
            password="test-password",
            first_name="Alex",
            last_name="Admin",
            role=User.Role.ADMIN,
        )

    def test_asset_representation_contains_nested_metadata(self):
        tag = Tag.objects.create(name="Athletics")
        collection = Collection.objects.create(
            name="Marathon",
            created_by=self.editor,
       )

        asset = self.make_asset(
        self.editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
            expiry_date=timezone.localdate() + timedelta(days=1),
        )

        asset.tags.add(tag)
        asset.collections.add(collection)

        data = AssetSerializer(asset).data

        self.assertEqual(data["id"], str(asset.id))
        self.assertEqual(data["title"], asset.title)
        self.assertEqual(data["uploader"]["email"], self.editor.email)
        self.assertEqual(data["approver"]["email"], self.admin.email)
        self.assertEqual(data["tags"][0]["name"], "Athletics")
        self.assertEqual(
            data["collections"][0]["name"],
            "Marathon",
        )
        self.assertFalse(data["is_expired"])
        self.assertTrue(data["is_viewer_accessible"])
        self.assertEqual(data["public_id"], asset.public_id)

    def test_update_changes_relationships_and_creates_event(self):
        original_tag = Tag.objects.create(name="Road")
        replacement_tag = Tag.objects.create(name="Track")

        collection = Collection.objects.create(
            name="Olympic Finals",
            created_by=self.editor,
        )

        asset = self.make_asset(self.editor)
        asset.tags.add(original_tag)

        original_public_id = asset.public_id

        request = APIRequestFactory().patch(
            f"/api/assets/{asset.pk}/"
        )
        request.user = self.editor

        serializer = AssetSerializer(
            instance=asset,
            data={
                "caption": "Updated race caption",
                "tag_ids": [replacement_tag.pk],
                "collection_ids": [collection.pk],
                "status": Asset.Status.APPROVED,
                "public_id": "forged-public-id",
            },
            partial=True,
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated_asset = serializer.save()

        self.assertEqual(
            updated_asset.caption,
            "Updated race caption",
        )
        self.assertEqual(
            list(updated_asset.tags.all()),
            [replacement_tag],
        )
        self.assertEqual(
            list(updated_asset.collections.all()),
            [collection],
        )

        self.assertEqual(
            updated_asset.status,
            Asset.Status.DRAFT,
        )
        self.assertEqual(
            updated_asset.public_id,
            original_public_id,
        )

        event = updated_asset.events.get(
            action=AssetEvent.Action.UPDATED
        )

        self.assertEqual(event.actor, self.editor)
        self.assertCountEqual(
            event.metadata["changed_fields"],
            ["caption", "tags", "collections"],
        )

class WorkflowAccessTests(AssetFactoryMixin, TestCase):
    def setUp(self):
        User = get_user_model()

        self.viewer = User.objects.create_user(
            email="access.viewer@example.com",
            password="test-password",
            role=User.Role.VIEWER,
        )
        self.editor = User.objects.create_user(
            email="access.editor@example.com",
            password="test-password",
            role=User.Role.EDITOR,
        )
        self.other_editor = User.objects.create_user(
            email="access.other@example.com",
            password="test-password",
            role=User.Role.EDITOR,
        )
        self.admin = User.objects.create_user(
            email="access.admin@example.com",
            password="test-password",
            role=User.Role.ADMIN,
        )
    def test_user_role_identifies_each_access_level(self):
        self.assertEqual(
            workflow_service.user_role(AnonymousUser()),
            "anonymous",
        )

        self.assertEqual(
            workflow_service.user_role(self.viewer),
            "viewer",
        )
        self.assertEqual(
            workflow_service.user_role(self.editor),
            "editor",
        )
        self.assertEqual(
            workflow_service.user_role(self.admin),
            "admin",
        )

    def test_editor_edits_only_own_editable_assets(self):
            own_draft = self.make_asset(
                self.editor,
                status=Asset.Status.DRAFT,
            )
            own_review = self.make_asset(
                self.editor,
                status=Asset.Status.IN_REVIEW,
            )
            other_draft = self.make_asset(
                self.other_editor,
                status=Asset.Status.DRAFT,
            )

            self.assertTrue(
                workflow_service.can_edit_metadata(
                    self.editor,
                    own_draft,
                )
            )

            self.assertFalse(
                workflow_service.can_edit_metadata(
                    self.editor,
                    own_review,
                )
            )

            self.assertFalse(
                workflow_service.can_edit_metadata(
                    self.editor,
                    other_draft,
                )
            )

            self.assertTrue(
                workflow_service.can_edit_metadata(
                    self.admin,
                    own_draft,
                )
            )

    def test_view_access_respects_owner_role_and_rights(self):
        approved_asset = self.make_asset(
            self.other_editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
        )

        hidden_draft = self.make_asset(
            self.other_editor,
            status=Asset.Status.DRAFT,
        )   

        own_draft = self.make_asset(
            self.editor,
            status=Asset.Status.DRAFT,
        )

        self.assertTrue(
            workflow_service.can_view(
                self.viewer,
                approved_asset,
            )
        )
        self.assertFalse(
            workflow_service.can_view(
                self.viewer,
                hidden_draft,
            )
        )
        self.assertTrue(
            workflow_service.can_view(
                self.editor,
                own_draft,
            )
        )
        self.assertFalse(
            workflow_service.can_view(
                self.editor,
                hidden_draft,
            )
        )
        self.assertTrue(
            workflow_service.can_view(
                self.admin,
                hidden_draft,
            )
        )


class TaxonomyAPITests(AssetFactoryMixin, APITestCase):
    def setUp(self):
        User = get_user_model()

        self.viewer = User.objects.create_user(
            email="taxonomy.viewer@example.com",
            password="test-password",
            role=User.Role.VIEWER,
        )
        self.editor = User.objects.create_user(
            email="taxonomy.editor@example.com",
            password="test-password",
            role=User.Role.EDITOR,
        )
        self.admin = User.objects.create_user(
            email="taxonomy.admin@example.com",
            password="test-password",
            role=User.Role.ADMIN,
        )

    def test_authentication_is_required(self):

        response = self.client.get(reverse("tag-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_lists_include_asset_counts(self):
        tag = Tag.objects.create(name="Athletics")
        collection = Collection.objects.create(
            name="Olympic Finals",
            created_by=self.editor,
        )

        asset = self.make_asset(self.editor)
        asset.tags.add(tag)
        asset.collections.add(collection)

        self.client.force_authenticate(self.viewer)

        tag_response = self.client.get(
            reverse("tag-list")
        )
        collection_response = self.client.get(
            reverse("collection-list")
        )

        self.assertEqual(tag_response.status_code, 200)
        self.assertEqual(collection_response.status_code, 200)
        self.assertEqual(
            tag_response.data[0]["asset_count"],
            1,
        )
        self.assertEqual(
            collection_response.data[0]["asset_count"],
            1,
        )

    def test_taxonomy_write_permissions(self):
        tag = Tag.objects.create(name="Athletics")

        self.client.force_authenticate(self.viewer)

        denied = self.client.post(
            reverse("tag-list"),
            {"name": "Cycling"},
            format="json",
        )

        self.assertIn(denied.status_code, (403, 405))

        self.client.force_authenticate(self.editor)

        created = self.client.post(
            reverse("collection-list"),
            {"name": "Paris Games", 
             "description": "Course demonstration."},
            format="json",
        )


        self.assertEqual(created.status_code, 201)

        collection = Collection.objects.get(
            pk=created.data["id"]
        )
        self.assertEqual(collection.created_by, self.editor)


        own_update = self.client.patch(
            reverse(
                "collection-detail",
                args=[collection.pk],
            ),
            {"description": "Updated description"},
            format="json",
        )

        self.assertEqual(own_update.status_code, 200)

        shared_tag_update = self.client.patch(
            reverse(
                "tag-detail",
                args=[tag.pk],
            ),
            {"name": "Track"},
            format="json",
        )   

        self.assertEqual(shared_tag_update.status_code, 403)

        self.client.force_authenticate(self.admin)

        admin_tag_update = self.client.patch(
            reverse(
                "tag-detail",
                args=[tag.pk],
            ),
            {"name": "Track"},
            format="json",
        )   

        self.assertEqual(admin_tag_update.status_code, 200)


class AssetAPITests(AssetFactoryMixin, APITestCase):    
    def setUp(self):
        User = get_user_model()

        self.viewer = User.objects.create_user(
            email="api.viewer@example.com",
            password="test-password",
            role=User.Role.VIEWER,
        )
        self.editor = User.objects.create_user(
            email="api.editor@example.com",
            password="test-password",
            role=User.Role.EDITOR,
        )
        self.other_editor = User.objects.create_user(
            email="api.other@example.com",
            password="test-password",
            role=User.Role.EDITOR,
        )
        self.admin = User.objects.create_user(
            email="api.admin@example.com",
            password="test-password",
            role=User.Role.ADMIN,
        )

    @staticmethod
    def results(response):
        """Return the list of asset IDs from a paginated API response."""
        return response.data.get(
            "results",
            response.data,
        )

    def test_authentication_is_required(self):
        response = self.client.get(reverse("asset-list"))
        self.assertIn(response.status_code, (401, 403)) 

    def test_viewer_sees_only_approved_usable_assets(self):
       visible = self.make_asset(
            self.other_editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
       )

       self.make_asset(
            self.editor,
            status=Asset.Status.DRAFT,
       )

       self.make_asset(
            self.other_editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
           expiry_date=timezone.localdate() - timedelta(days=1),
       )    

       self.make_asset(
            self.editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
            permitted_use=Asset.PermittedUse.INTERNAL,
        )

       self.client.force_authenticate(self.viewer)

       response = self.client.get(
            reverse("asset-list")
        )
       self.assertEqual(response.status_code, 200)
       ids = {
            item["id"]
            for item in self.results(response)
        }

       self.assertEqual(ids, {str(visible.pk)})


    def test_editor_sees_own_assets_and_approved_usable(self):
        own_draft = self.make_asset(
            self.editor,
            status=Asset.Status.DRAFT,
        )
        public_asset = self.make_asset(
            self.other_editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
        )

        hidden_asset = self.make_asset(
            self.other_editor,
            status=Asset.Status.DRAFT,
        )

        self.client.force_authenticate(self.editor)

        response = self.client.get(
            reverse("asset-list")
        )
        self.assertEqual(response.status_code, 200)
        ids = {
            item["id"]
            for item in self.results(response)
        }

        self.assertIn(str(own_draft.pk), ids)
        self.assertIn(str(public_asset.pk), ids)
        self.assertNotIn(str(hidden_asset.pk), ids)

    def test_editor_can_patch_own_draft_but_not_another_asset(self):
        own_draft = self.make_asset(
            self.editor,
            status=Asset.Status.DRAFT,
        )

        other_asset = self.make_asset(
            self.other_editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
        )

        self.client.force_authenticate(self.editor)

        own_response = self.client.patch(
            reverse(
                "asset-detail",
                args=[own_draft.pk],
            ),
            {"caption": "Updated through the API"},
            format="json",
        )

        other_response = self.client.patch(
            reverse(
                "asset-detail",
                args=[other_asset.pk],
            ),
            {"caption": "Unauthorised change"},
            format="json",
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(other_response.status_code, 403)

        own_draft.refresh_from_db()

        self.assertEqual(
            own_draft.caption,
            "Updated through the API",
        )
        self.assertTrue(
            own_draft.events.filter(
                action=AssetEvent.Action.UPDATED
            ).exists()
        )

    def test_expired_asset_returns_not_found_to_viewer(self):
        expired_asset = self.make_asset(
            self.editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
            expiry_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
        )

        self.client.force_authenticate(self.viewer)

        response = self.client.get(
            reverse(
                "asset-detail",
                args=[expired_asset.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_dashboard_is_role_aware(self):
        approved_asset = self.make_asset(
            self.editor,
            status=Asset.Status.APPROVED,
            approver=self.admin,
            approved_at=timezone.now(),
            expiry_date=(
                timezone.localdate()
                + timedelta(days=10)
            ),
        )

        self.make_asset(
            self.editor,
            status=Asset.Status.IN_REVIEW,
        )

        self.make_asset(
            self.editor,
            status=Asset.Status.DRAFT,
            alt_text="",
        )

        self.client.force_authenticate(self.admin)

        admin_response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(admin_response.status_code, 200)

        self.assertEqual(
            admin_response.data["total_assets"],
            3,
        )
        self.assertEqual(
            admin_response.data["pending_review_count"],
            1,
        )
        self.assertEqual(
            admin_response.data["missing_metadata_count"],
            1,
        )
        self.assertEqual(
            admin_response.data["expiring_rights_count"],
            1,
        )

        self.assertEqual(
            admin_response.data["status_breakdown"]["in_review"],
            1,
        )

        self.client.force_authenticate(self.viewer)

        viewer_response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(
            viewer_response.status_code,
            200,
        )
        self.assertEqual(
            viewer_response.data["total_assets"],
            1,
        )
        self.assertEqual(
            viewer_response.data["pending_review_count"],
            0,
        )
        self.assertEqual(
            viewer_response.data["recent_assets"][0]["id"],
            str(approved_asset.pk),
        )

class CloudinaryServiceTests(TestCase):
    def test_validation_checks_bytes_not_extension(self):
        disguised_text = SimpleUploadedFile(
            "looks-valid.jpg",
            b"this is not an image",
            content_type="image/jpeg",
        )

        with self.assertRaisesRegex(
            cloudinary_service.ImageValidationError,
            "not a valid image",
        ):
            cloudinary_service.validate_image(
                disguised_text
            )

    def test_validation_accepts_image_and_rewinds_file(self):
        uploaded = image_upload()

        image_format = (
            cloudinary_service.validate_image(
                uploaded
            )
        )

        self.assertEqual(image_format, "png")
        self.assertEqual(uploaded.tell(), 0)

    def test_validation_rejects_files_over_ten_megabytes(self):
        uploaded = SimpleUploadedFile(
            "large.png",
            b"small placeholder",
            content_type="image/png",
        )
        uploaded.size = (
            cloudinary_service.MAX_UPLOAD_BYTES + 1
        )

        with self.assertRaisesRegex(
            cloudinary_service.ImageValidationError,
            "10 MB",
        ):
            cloudinary_service.validate_image(
                uploaded
            )

    @override_settings(
        CLOUDINARY_STORAGE={
            "CLOUD_NAME": "course-cloud",
            "API_KEY": "test-key",
            "API_SECRET": "test-secret",
        }
        CLOUDINARY_URL="",)
