from __future__ import annotations

from django.db import models

from orders.models import Order


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
        "customers.Address",
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
