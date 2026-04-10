from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product
from .models import Cart, CartItem, Order, OrderItem, PromoCode


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_primary_image = serializers.SerializerMethodField()
    product_primary_image_alt_text = serializers.SerializerMethodField()
    product_stock_quantity = serializers.IntegerField(source="product.stock_quantity", read_only=True)
    product_is_in_stock = serializers.BooleanField(source="product.is_in_stock", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_primary_image",
            "product_primary_image_alt_text",
            "product_stock_quantity",
            "product_is_in_stock",
            "quantity",
            "unit_price",
            "total_price",
        ]
        read_only_fields = ["id", "unit_price", "total_price", "product_id", "product_name"]

    def get_product_primary_image(self, obj):
        primary = obj.product.images.filter(is_primary=True).first() or obj.product.images.first()
        return primary.image.url if primary else None

    def get_product_primary_image_alt_text(self, obj):
        primary = obj.product.images.filter(is_primary=True).first() or obj.product.images.first()
        return primary.alt_text if primary else None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "session_id", "is_active", "created_at", "updated_at", "items", "subtotal", "total"]
        read_only_fields = ["id", "user", "session_id", "created_at", "updated_at", "items", "subtotal", "total"]


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "product_name", "quantity", "unit_price", "total_price"]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address_id = serializers.IntegerField(source="shipping_address.id", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "subtotal",
            "tax",
            "shipping_cost",
            "shipping_address_id",
            "total",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=4, required=False, default=Decimal("0.0000"))
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=Decimal("0.00"))
    address_id = serializers.IntegerField(required=False)


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ["id", "code", "discount_type", "value", "expires_at", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


def create_order_from_cart(*, cart: Cart, user, tax_rate: Decimal, shipping_cost: Decimal, shipping_address=None) -> Order:
    if not cart.is_active:
        raise serializers.ValidationError({"cart": "Cart is not active."})

    items = list(cart.items.select_related("product").all())
    if not items:
        raise serializers.ValidationError({"cart": "Cart is empty."})

    subtotal = sum((item.total_price for item in items), Decimal("0.00"))
    tax = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total = (subtotal + tax + shipping_cost).quantize(Decimal("0.01"))

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            status=Order.Status.PENDING,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            shipping_address=shipping_address,
            total=total,
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                )
                for item in items
            ]
        )
        cart.is_active = False
        cart.save(update_fields=["is_active", "updated_at"])

    return order
