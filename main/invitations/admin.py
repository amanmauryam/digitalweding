from django.contrib import admin

from .models import (
    CustomerEvent,
    EventFunction,
    GuestBlessing,
    InvitationCategory,
    LeadCapture,
    RSVPResponse,
    TemplateTheme,
)


@admin.register(InvitationCategory)
class InvitationCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(TemplateTheme)
class TemplateThemeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "style_type", "is_active")
    list_filter = ("category", "style_type", "is_active")
    search_fields = ("title", "template_code")


class EventFunctionInline(admin.TabularInline):
    model = EventFunction
    extra = 1
    fields = ("function_code", "function_name", "date_and_time", "venue_name", "address")


class RSVPInline(admin.TabularInline):
    model = RSVPResponse
    extra = 0
    readonly_fields = ("submitted_at",)
    fields = ("guest_name", "guest_phone", "guest_family_tag", "attending_status", "guest_count")


@admin.register(CustomerEvent)
class CustomerEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_title",
        "bride_name",
        "groom_name",
        "wedding_date",
        "user",
        "view_count",
        "is_published",
    )
    list_filter = ("is_published", "primary_language", "wedding_date")
    search_fields = ("event_title", "bride_name", "groom_name", "slug", "host_phone")
    fieldsets = (
        (None, {"fields": ("bride_name", "groom_name", "event_title", "slug", "wedding_date")}),
        ("Bihari Host Context", {"fields": ("family_head_name", "native_place", "host_phone", "primary_language")}),
        ("Content", {"fields": ("template", "custom_shloka", "welcome_message")}),
        ("Analytics", {"fields": ("user", "view_count", "is_published", "created_at")}),
    )
    readonly_fields = ("view_count", "created_at")
    inlines = [EventFunctionInline, RSVPInline]


@admin.register(EventFunction)
class EventFunctionAdmin(admin.ModelAdmin):
    list_display = ("function_name", "function_code", "event", "date_and_time", "venue_name")
    list_filter = ("function_code",)


@admin.register(RSVPResponse)
class RSVPResponseAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "guest_phone", "event", "attending_status", "guest_count")
    list_filter = ("attending_status", "event")
    search_fields = ("guest_name", "guest_phone", "guest_family_tag")


@admin.register(GuestBlessing)
class GuestBlessingAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "kind", "event", "created_at")
    list_filter = ("kind",)


@admin.register(LeadCapture)
class LeadCaptureAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "name", "district", "event_date", "source", "is_contacted")
    list_filter = ("is_contacted", "source")
    list_editable = ("is_contacted",)
    search_fields = ("phone_number", "name", "district")
