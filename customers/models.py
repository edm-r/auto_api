from __future__ import annotations

from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserProfile({self.user_id})"


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=32, blank=True)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=2, default="CM")
    postal_code = models.CharField(max_length=20, blank=True)
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
        return f"Address({self.pk})"


class WishList(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )
    products = models.ManyToManyField("products.Product", blank=True, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WishList({self.user_id})"


class VehiclePreference(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicle_preferences",
    )
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(null=True, blank=True)
    engine_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"VehiclePreference({self.pk})"

