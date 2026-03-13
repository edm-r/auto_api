from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "session_id", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["session_id", "user__username", "user__email"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "cart", "product", "quantity", "unit_price", "total_price"]
    search_fields = ["cart__id", "product__name", "product__sku"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "subtotal", "tax", "shipping_cost", "total", "created_at"]
    list_filter = ["status"]
    search_fields = ["id", "user__username", "user__email"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "unit_price", "total_price"]
    search_fields = ["order__id", "product__name", "product__sku"]

