from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import OrderSerializer
from products.models import Product

from .models import Address, UserProfile, VehiclePreference, WishList
from .serializers import (
    AddressSerializer,
    UserProfileSerializer,
    VehiclePreferenceSerializer,
    WishListItemSerializer,
    WishListSerializer,
)


User = get_user_model()


class ProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data, status=status.HTTP_200_OK)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            address = serializer.save(user=self.request.user)
            if address.is_default:
                Address.objects.filter(user=address.user).exclude(pk=address.pk).update(is_default=False)

    def perform_update(self, serializer):
        with transaction.atomic():
            address = serializer.save()
            if address.is_default:
                Address.objects.filter(user=address.user).exclude(pk=address.pk).update(is_default=False)


class WishListViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        wishlist, _ = WishList.objects.get_or_create(user=request.user)
        return Response(WishListSerializer(wishlist).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def add(self, request):
        wishlist, _ = WishList.objects.get_or_create(user=request.user)
        serializer = WishListItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(pk=serializer.validated_data["product_id"])
        wishlist.products.add(product)
        return Response(WishListSerializer(wishlist).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        wishlist, _ = WishList.objects.get_or_create(user=request.user)
        serializer = WishListItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wishlist.products.remove(serializer.validated_data["product_id"])
        return Response(WishListSerializer(wishlist).data, status=status.HTTP_200_OK)


class VehiclePreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = VehiclePreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = VehiclePreference.objects.all()
        user = self.request.user
        if getattr(user, "is_staff", False):
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_staff", False):
            return Order.objects.all().prefetch_related("items", "items__product")
        return Order.objects.filter(user=user).prefetch_related("items", "items__product")
