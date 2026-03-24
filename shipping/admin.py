from django.contrib import admin

from .models import Shipment, ShippingAddress


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "city", "country", "is_default", "updated_at")
    list_filter = ("country", "is_default")
    search_fields = ("full_name", "city", "postal_code", "address_line1", "user__username", "user__email")


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "carrier", "tracking_number", "updated_at")
    list_filter = ("status", "carrier")
    search_fields = ("tracking_number", "order__id", "order__user__username", "order__user__email")
