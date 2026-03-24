from __future__ import annotations

from rest_framework import serializers

from products.models import Product
from .models import Address, UserProfile, VehiclePreference, WishList


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["phone_number", "avatar", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "full_name",
            "phone_number",
            "address_line",
            "city",
            "region",
            "country",
            "postal_code",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WishListSerializer(serializers.ModelSerializer):
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        source="products",
    )

    class Meta:
        model = WishList
        fields = ["product_ids", "created_at"]
        read_only_fields = fields


class WishListItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product not found.")
        return value


class VehiclePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePreference
        fields = ["id", "brand", "model", "year", "engine_type", "created_at"]
        read_only_fields = ["id", "created_at"]

