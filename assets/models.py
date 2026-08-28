
# Create your models here.

"""Database models for Streamline's image catalogue"""

from __future__ import annotations
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class NamedSlugModel(models.Model):
    """Abstract model for named objects with a slug field."""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True),

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
        UNKNOWN = "unknown", "Unknown",
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
    title = models.CharField(max_length=255)

    caption = models.TextField(blank=True)

    alt_text = models.TextField(blank=True)

    photographer_credit = models.CharField(max_length=255, blank=True)

    event_name = models.CharField(max_length=255, blank=True)

    location = models.CharField(max_length=255, blank=True)

    captured_at = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="assets")

    collections = models.ManyToManyField(
        Collection, blank=True, related_name="assets",
    )