from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from customers.models import Address
from products.models import Product
from .models import Cart, CartItem, Order
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderSerializer,
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
    return cart


class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        cart = get_or_create_active_cart(request)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

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
            shipping_address = get_object_or_404(Address, pk=address_id, user=request.user)

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
