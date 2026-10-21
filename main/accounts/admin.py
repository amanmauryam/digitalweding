from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class DigitalWeddingUserAdmin(UserAdmin):
    list_display = ("username", "full_name", "phone_number", "home_district", "is_staff")
    list_filter = ("home_district", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("Bihar Context", {"fields": ("phone_number", "home_district", "is_business_lead")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Bihar Context", {"fields": ("phone_number", "home_district")}),
    )

    @admin.display(description="Full Name")
    def full_name(self, obj):
        return obj.get_full_name() or obj.username
