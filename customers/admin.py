from django.contrib import admin

from .models import Address, UserProfile, VehiclePreference, WishList


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number", "updated_at")
    search_fields = ("user__username", "user__email", "phone_number")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "city", "country", "is_default", "updated_at")
    list_filter = ("country", "is_default")
    search_fields = ("full_name", "city", "postal_code", "address_line", "user__username", "user__email")


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")


@admin.register(VehiclePreference)
class VehiclePreferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "brand", "model", "year", "engine_type", "created_at")
    list_filter = ("brand", "engine_type")
    search_fields = ("user__username", "user__email", "brand", "model")

