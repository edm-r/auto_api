from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from customers.models import Address
from .models import Shipment
from .serializers import AddressSerializer, CreateShipmentSerializer, ShipmentSerializer


class ShippingAddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Address.objects.all()
        user = self.request.user
        if getattr(user, "is_staff", False):
            return qs
        return qs.filter(user=user)

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


class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        qs = Shipment.objects.select_related("order", "order__user", "address", "address__user")
        user = self.request.user
        if getattr(user, "is_staff", False):
            return qs
        return qs.filter(order__user=user)

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "mark_shipped", "mark_delivered"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateShipmentSerializer
        return ShipmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data["order"]
        address = serializer.validated_data["address"]

        with transaction.atomic():
            if Shipment.objects.filter(order=order).exists():
                return Response({"detail": "Shipment already exists for this order."}, status=status.HTTP_400_BAD_REQUEST)

            shipment = Shipment.objects.create(
                order=order,
                address=address,
                carrier=serializer.validated_data.get("carrier", ""),
                tracking_number=serializer.validated_data.get("tracking_number", ""),
                status=Shipment.Status.PENDING,
            )

        out = ShipmentSerializer(shipment)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_shipped(self, request, pk=None):
        shipment = self.get_object()
        carrier = request.data.get("carrier", shipment.carrier)
        tracking_number = request.data.get("tracking_number", shipment.tracking_number)

        with transaction.atomic():
            shipment.carrier = carrier or ""
            shipment.tracking_number = tracking_number or ""
            shipment.status = Shipment.Status.SHIPPED
            if shipment.shipped_at is None:
                shipment.shipped_at = timezone.now()
            shipment.save(update_fields=["carrier", "tracking_number", "status", "shipped_at", "updated_at"])

            order = shipment.order
            order.status = Order.Status.SHIPPED
            order.save(update_fields=["status", "updated_at"])

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def mark_delivered(self, request, pk=None):
        shipment = self.get_object()
        with transaction.atomic():
            shipment.status = Shipment.Status.DELIVERED
            if shipment.delivered_at is None:
                shipment.delivered_at = timezone.now()
            shipment.save(update_fields=["status", "delivered_at", "updated_at"])

            order = shipment.order
            order.status = Order.Status.DELIVERED
            order.save(update_fields=["status", "updated_at"])

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)
