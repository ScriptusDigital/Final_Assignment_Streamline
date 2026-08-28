from django.db import models

# Create your models here.

"""Database models for Streamline's image catalogue"""

from __future__ import annotations

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

            description = models.TextField(blank=True, null=True)   

            created_by = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name="asset_collections",
            )