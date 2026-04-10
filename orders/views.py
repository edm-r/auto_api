from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from customers.models import Address
from products.models import Product
from .models import Cart, CartItem, Order, PromoCode
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
    PromoCodeSerializer,
    UpdateCartItemSerializer,
    create_order_from_cart,
)


def _get_session_id(request) -> str:
    header_session = request.headers.get("X-Session-Id")
    if header_session:
        return header_session

    # Ensure a session exists for anonymous carts.
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_or_create_active_cart(request) -> Cart:
    user = getattr(request, "user", None)
    if user and not isinstance(user, AnonymousUser) and getattr(user, "is_authenticated", False):
        user_cart, _ = Cart.objects.get_or_create(user=user, is_active=True, defaults={"session_id": ""})
        user_cart = Cart.objects.prefetch_related("items", "items__product", "items__product__images").get(pk=user_cart.pk)

        # If the user had an anonymous cart on the current session, merge it.
        session_id = request.headers.get("X-Session-Id") or getattr(request.session, "session_key", None)
        if session_id:
            anon_cart = (
                Cart.objects.filter(user__isnull=True, session_id=session_id, is_active=True)
                .prefetch_related("items", "items__product")
                .first()
            )
            if anon_cart and anon_cart.id != user_cart.id and anon_cart.items.exists():
                with transaction.atomic():
                    for anon_item in anon_cart.items.select_related("product").select_for_update():
                        dest_item, created = CartItem.objects.select_for_update().get_or_create(
                            cart=user_cart,
                            product=anon_item.product,
                            defaults={
                                "quantity": anon_item.quantity,
                                "unit_price": anon_item.product.price,
                                "total_price": anon_item.product.price * anon_item.quantity,
                            },
                        )
                        if not created:
                            dest_item.quantity += anon_item.quantity
                            dest_item.unit_price = anon_item.product.price
                            dest_item.save()

                    anon_cart.is_active = False
                    anon_cart.save(update_fields=["is_active", "updated_at"])

        return user_cart

    session_id = _get_session_id(request)
    cart, _ = Cart.objects.get_or_create(user=None, session_id=session_id, is_active=True)
    cart = Cart.objects.prefetch_related("items", "items__product", "items__product__images").get(pk=cart.pk)
    return cart


class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        cart = get_or_create_active_cart(request)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="promo/validate")
    def validate_promo(self, request):
        cart = get_or_create_active_cart(request)
        code = (request.data or {}).get("code", "")
        code = str(code).strip().upper()

        if not code:
            return Response({"valid": False, "detail": "Promo code is required."}, status=status.HTTP_200_OK)

        subtotal = Decimal(str(getattr(cart, "subtotal", "0.00")))

        promo = PromoCode.objects.filter(code=code).first()
        if promo is None:
            # Backward compatibility for existing demo code.
            if code != "AUTO10":
                return Response({"valid": False, "detail": "Invalid promo code."}, status=status.HTTP_200_OK)
            discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
            total_after_discount = (subtotal - discount).quantize(Decimal("0.01"))
            return Response(
                {
                    "valid": True,
                    "code": code,
                    "discount_type": "percent",
                    "discount_percent": "10",
                    "discount_amount": str(discount),
                    "subtotal": str(subtotal),
                    "total_after_discount": str(total_after_discount),
                },
                status=status.HTTP_200_OK,
            )

        if not promo.is_valid():
            return Response({"valid": False, "detail": "Promo code is expired or inactive."}, status=status.HTTP_200_OK)

        if promo.discount_type == PromoCode.DiscountType.PERCENT:
            percent = promo.value
            discount = (subtotal * (percent / Decimal("100"))).quantize(Decimal("0.01"))
            total_after_discount = (subtotal - discount).quantize(Decimal("0.01"))
            return Response(
                {
                    "valid": True,
                    "code": promo.code,
                    "discount_type": promo.discount_type,
                    "discount_percent": str(percent),
                    "discount_amount": str(discount),
                    "subtotal": str(subtotal),
                    "total_after_discount": str(total_after_discount),
                },
                status=status.HTTP_200_OK,
            )

        # fixed amount
        discount = promo.value.quantize(Decimal("0.01"))
        if discount > subtotal:
            discount = subtotal
        total_after_discount = (subtotal - discount).quantize(Decimal("0.01"))
        return Response(
            {
                "valid": True,
                "code": promo.code,
                "discount_type": promo.discount_type,
                "discount_amount": str(discount),
                "subtotal": str(subtotal),
                "total_after_discount": str(total_after_discount),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        if not getattr(request.user, "is_authenticated", False):
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        cart = get_or_create_active_cart(request)
        serializer = CheckoutSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)

        shipping_address = None
        address_id = serializer.validated_data.get("address_id")
        if address_id is not None:
            shipping_address = Address.objects.filter(pk=address_id, user=request.user).first()
            if shipping_address is None:
                payload = {"detail": "Invalid address_id for this user."}
                if getattr(settings, "DEBUG", False):
                    payload.update(
                        {
                            "user_id": getattr(request.user, "id", None),
                            "available_address_ids": list(
                                Address.objects.filter(user=request.user).values_list("id", flat=True)
                            ),
                        }
                    )
                return Response(
                    payload,
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order = create_order_from_cart(
            cart=cart,
            user=request.user,
            tax_rate=serializer.validated_data["tax_rate"],
            shipping_cost=serializer.validated_data["shipping_cost"],
            shipping_address=shipping_address,
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        cart = get_or_create_active_cart(request)
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, pk=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity, "unit_price": product.price, "total_price": product.price * quantity},
            )
            if not created:
                item.quantity += quantity
                item.unit_price = product.price
                item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        cart = get_or_create_active_cart(request)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.quantity = serializer.validated_data["quantity"]
        item.save()
        return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        cart = get_or_create_active_cart(request)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_staff", False):
            return Order.objects.all().prefetch_related("items", "items__product")
        return Order.objects.filter(user=user).prefetch_related("items", "items__product")

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser], url_path="update-status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        next_status = (request.data or {}).get("status", "")
        next_status = str(next_status).strip()

        valid = {choice[0] for choice in Order.Status.choices}
        if next_status not in valid:
            return Response(
                {"detail": "Invalid status.", "valid_statuses": sorted(valid)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = next_status
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class PromoCodeViewSet(viewsets.ModelViewSet):
    serializer_class = PromoCodeSerializer
    permission_classes = [IsAdminUser]
    queryset = PromoCode.objects.all()
