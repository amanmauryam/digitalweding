from django.contrib import admin

from .models import WeddingEvent, WeddingPhoto, WeddingRSVP, WeddingWebsite


class WeddingEventInline(admin.TabularInline):
    model = WeddingEvent
    extra = 0


class WeddingPhotoInline(admin.TabularInline):
    model = WeddingPhoto
    extra = 0


@admin.register(WeddingWebsite)
class WeddingWebsiteAdmin(admin.ModelAdmin):
    list_display = (
        "display_title",
        "owner",
        "status",
        "wedding_date",
        "theme",
        "view_count",
        "created_at",
    )
    list_filter = ("status", "theme", "language")
    search_fields = ("groom_name", "bride_name", "title", "slug", "owner__username")
    readonly_fields = ("slug", "created_at", "updated_at", "published_at", "view_count")
    inlines = [WeddingEventInline, WeddingPhotoInline]
    exclude = ("source_text",)


@admin.register(WeddingEvent)
class WeddingEventAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "date", "start_time", "venue")
    list_filter = ("website",)
    search_fields = ("name", "venue")


@admin.register(WeddingPhoto)
class WeddingPhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "website", "kind", "created_at")
    list_filter = ("kind", "website")


@admin.register(WeddingRSVP)
class WeddingRSVPAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "website", "attending", "guest_count", "created_at")
    list_filter = ("attending", "website")
    search_fields = ("guest_name", "guest_phone")
