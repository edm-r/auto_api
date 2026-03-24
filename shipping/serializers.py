from __future__ import annotations

from rest_framework import serializers

from orders.models import Order
from .models import Shipment, ShippingAddress


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "id",
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    address_id = serializers.IntegerField(source="address.id", read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order_id",
            "address_id",
            "carrier",
            "tracking_number",
            "status",
            "shipped_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "order_id", "address_id", "created_at", "updated_at"]


class CreateShipmentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    address_id = serializers.IntegerField()
    carrier = serializers.CharField(required=False, allow_blank=True, max_length=80)
    tracking_number = serializers.CharField(required=False, allow_blank=True, max_length=120)

    def validate(self, attrs):
        order = Order.objects.filter(pk=attrs["order_id"]).select_related("user").first()
        if order is None:
            raise serializers.ValidationError({"order_id": "Order not found."})

        address = ShippingAddress.objects.filter(pk=attrs["address_id"]).select_related("user").first()
        if address is None:
            raise serializers.ValidationError({"address_id": "Address not found."})

        if address.user_id != order.user_id:
            raise serializers.ValidationError({"address_id": "Address does not belong to the order owner."})

        attrs["order"] = order
        attrs["address"] = address
        return attrs

