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