from django.contrib import admin

from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "carrier", "tracking_number", "updated_at")
    list_filter = ("status", "carrier")
    search_fields = ("tracking_number", "order__id", "order__user__username", "order__user__email")
