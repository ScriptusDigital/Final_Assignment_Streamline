from django.contrib import admin

from .models import Asset, AssetEvent, Collection, Tag



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at",
    )
    search_fields = ("name", "description",
    )
    prepopulated_fields = {"slug": ("name",),
    }


class AssetEventInline(admin.TabularInline):
    model = AssetEvent
    extra = 0
    can_delete = False
    readonly_fields = (
        "actor",
        "action",
        "from_status",
        "to_status",
        "message",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
         "title",
        "status",
        "rights_status",
        "uploader",
        "expiry_date",
        "created_at",
    )
    list_filter = (
        "status",
        "rights_status",
        "permitted_use",
        "created_at",
    )
    search_fields = (
        "title",
        "caption",
        "alt_text",
        "event_name",
        "public_id",
    )
    autocomplete_fields = (
        "uploader",
        "approver",
    )
    filter_horizontal = (
        "tags",
        "collections",
    )
    readonly_fields = (
        "id",
        "cloudinary_asset_id",
        "public_id",
        "secure_url",
        "image_format",
        "width",
        "height",
        "bytes",
        "version",
        "created_at",
        "updated_at",
    )
    inlines = (AssetEventInline,)


@admin.register(AssetEvent)
class AssetEventAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "action",
        "actor",
        "from_status",
        "to_status",
        "created_at",
    )
    list_filter = (
        "action",
        "created_at",
    )
    search_fields = (
        "asset__title",
        "actor__email",
        "message",
    )
    readonly_fields = (
        "asset",
        "actor",
        "action",
        "from_status",
        "to_status",
        "message",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False