
# Create your models here.

"""Database models for Streamline's image catalogue"""

from __future__ import annotations
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class NamedSlugModel(models.Model):
    """Abstract model for named objects with a slug field."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:80] or "item"
            candidate = base
            suffix = 2


            while (
                type(self)
                .objects.exclude(pk=self.pk)
                .filter(slug=candidate)
                .exists()
            ):
                candidate = f"{base[:75]}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
            return self.name

class Tag(NamedSlugModel):
            """Model for tags associated with images."""

class Collection(NamedSlugModel):
            """Model for collections of images."""

            description = models.TextField(blank=True)   

            created_by = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name="asset_collections",
            )


class Asset(models.Model):
    """Model for assets (images) in the catalogue."""
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In Review"
        CHANGES_REQUESTED = ("changes_requested", "Changes Requested")
        APPROVED = "approved", "Approved"
        ARCHIVED = "archived", "Archived"

    class RightsStatus(models.TextChoices):
        UNKNOWN = "unknown", "Not assessed",
        CLEARED = "cleared", "Cleared",
        RESTRICTED = "restricted", "Restricted",
        EXPIRED = "expired", "Expired"

    class PermittedUse(models.TextChoices):
        INTERNAL = "internal", "Internal use only"
        EDITORIAL = "editorial", "Editorial"
        MARKETING = "marketing", "Marketing"
        ALL = "all", "All approved uses"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #editorial metadata
    title = models.CharField(max_length=180)

    alt_text = models.CharField(max_length=300, blank=True, help_text=("Alternative text for accessibility and SEO"),)
    

    caption = models.TextField(blank=True)


    photographer_credit = models.CharField(max_length=180, blank=True)

    event_name = models.CharField(max_length=180, blank=True)

    location = models.CharField(max_length=180, blank=True)

    captured_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="assets")

    collections = models.ManyToManyField(
        Collection, blank=True, related_name="assets",
    )


    #Rights metadata
    rights_status = models.CharField(
        max_length=20,
        choices=RightsStatus.choices,
        default=RightsStatus.UNKNOWN,
    )

    permitted_use = models.CharField(
        max_length=20,
        choices=PermittedUse.choices,
        default=PermittedUse.INTERNAL,
    )

    licence_details = models.TextField(blank=True)

    expiry_date = models.DateField(null=True, blank=True)

    #Workflow metadata
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_assets",
    )

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_assets",
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)


#Storage respose data (Cloudinary  )

    cloudinary_asset_id = models.CharField(max_length=255, unique=True)

    public_id = models.CharField(max_length=255, unique=True)

    delivery_type = models.CharField(max_length=30, default="authenticated")

    secure_url = models.URLField(
            max_length=1000,
        )
    original_filename = models.CharField(
            max_length=255,
            blank=True,
        )
    image_format = models.CharField(
            max_length=20,
        )
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    bytes = models.PositiveBigIntegerField()
    version = models.PositiveBigIntegerField(
            null=True,
            blank=True,
        )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            ordering = ("-created_at",)
            indexes = [
                models.Index(  fields=("status", "-created_at"),name="asset_status_created_idx",
                ),
                models.Index(fields=("uploader", "status"),name="asset_owner_status_idx",
                ),
                models.Index(fields=("rights_status", "expiry_date"),name="asset_rights_expiry_idx",
                ),
                models.Index(fields=("expiry_date",),name="asset_expiry_idx",
                ),
            ]

    def __str__(self):
        return self.title