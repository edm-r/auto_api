from __future__ import annotations

from django.conf import settings
from django.db import models

from orders.models import Order


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shipping_addresses",
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=32, blank=True)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default="CM")

    is_default = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]
        indexes = [
            models.Index(fields=["user", "is_default"]),
            models.Index(fields=["user", "updated_at"]),
        ]

    def __str__(self):
        return f"ShippingAddress({self.pk})"


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELED = "canceled", "Canceled"

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="shipment",
    )
    address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.PROTECT,
        related_name="shipments",
    )
    carrier = models.CharField(max_length=80, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True, db_index=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "updated_at"]),
            models.Index(fields=["tracking_number"]),
        ]

    def __str__(self):
        return f"Shipment({self.pk})"
