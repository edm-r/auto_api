from decimal import Decimal

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework import status
from rest_framework.test import force_authenticate

from orders.models import Cart, Order
from orders.views import CartItemViewSet, CartViewSet, OrderViewSet
from products.models import Brand, Category, Product


def _add_session_to_request(request):
    middleware = SessionMiddleware(lambda _req: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.fixture
def product(db):
    category = Category.objects.create(name="CartCat")
    brand = Brand.objects.create(name="CartBrand")
    return Product.objects.create(
        name="Cart Product",
        sku="CART-001",
        description="Cart product",
        category=category,
        brand=brand,
        price=Decimal("10.00"),
        stock_quantity=100,
    )


@pytest.mark.django_db
def test_list_success(api_request_factory):
    request = api_request_factory.get("/api/cart/")
    _add_session_to_request(request)
    view = CartViewSet.as_view({"get": "list"})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] is not None
    assert response.data["is_active"] is True
    assert response.data["session_id"] != ""
    assert response.data["subtotal"] == "0.00"
    assert response.data["total"] == "0.00"


@pytest.mark.django_db
def test_create_success(api_request_factory, product):
    request = api_request_factory.post("/api/cart/items/", {"product_id": product.id, "quantity": 2}, format="json")
    _add_session_to_request(request)
    view = CartItemViewSet.as_view({"post": "create"})

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["product_id"] == product.id
    assert response.data["quantity"] == 2
    assert response.data["unit_price"] == "10.00"
    assert response.data["total_price"] == "20.00"


@pytest.mark.django_db
def test_partial_update_success(api_request_factory, product):
    # Create item
    create_req = api_request_factory.post(
        "/api/cart/items/",
        {"product_id": product.id, "quantity": 1},
        format="json",
    )
    _add_session_to_request(create_req)
    create_view = CartItemViewSet.as_view({"post": "create"})
    create_resp = create_view(create_req)
    item_id = create_resp.data["id"]

    # Update item quantity
    update_req = api_request_factory.patch("/api/cart/items/1/", {"quantity": 5}, format="json")
    update_req.session = create_req.session
    update_view = CartItemViewSet.as_view({"patch": "partial_update"})

    response = update_view(update_req, pk=item_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["quantity"] == 5
    assert response.data["total_price"] == "50.00"


@pytest.mark.django_db
def test_destroy_success(api_request_factory, product):
    create_req = api_request_factory.post(
        "/api/cart/items/",
        {"product_id": product.id, "quantity": 1},
        format="json",
    )
    _add_session_to_request(create_req)
    create_view = CartItemViewSet.as_view({"post": "create"})
    create_resp = create_view(create_req)
    item_id = create_resp.data["id"]

    delete_req = api_request_factory.delete("/api/cart/items/1/")
    delete_req.session = create_req.session
    delete_view = CartItemViewSet.as_view({"delete": "destroy"})

    response = delete_view(delete_req, pk=item_id)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_checkout_unauthenticated(api_request_factory, product):
    create_req = api_request_factory.post(
        "/api/cart/items/",
        {"product_id": product.id, "quantity": 1},
        format="json",
    )
    _add_session_to_request(create_req)
    CartItemViewSet.as_view({"post": "create"})(create_req)

    checkout_req = api_request_factory.post("/api/cart/checkout/", {}, format="json")
    checkout_req.session = create_req.session
    view = CartViewSet.as_view({"post": "checkout"})

    response = view(checkout_req)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_checkout_success(api_request_factory, make_user, product):
    user = make_user(username="buyer", email="buyer@example.com", is_staff=False)

    create_req = api_request_factory.post(
        "/api/cart/items/",
        {"product_id": product.id, "quantity": 2},
        format="json",
    )
    _add_session_to_request(create_req)
    CartItemViewSet.as_view({"post": "create"})(create_req)

    checkout_req = api_request_factory.post(
        "/api/cart/checkout/",
        {"tax_rate": "0.1000", "shipping_cost": "5.00"},
        format="json",
    )
    checkout_req.session = create_req.session
    force_authenticate(checkout_req, user=user)
    view = CartViewSet.as_view({"post": "checkout"})

    response = view(checkout_req)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"] == user.id
    assert response.data["status"] == "pending"
    assert response.data["subtotal"] == "20.00"
    assert response.data["tax"] == "2.00"
    assert response.data["shipping_cost"] == "5.00"
    assert response.data["total"] == "27.00"
    assert len(response.data["items"]) == 1

    assert Order.objects.filter(user=user).count() == 1
    assert Cart.objects.filter(is_active=True, user=user).count() == 0


@pytest.mark.django_db
def test_get_queryset_edge_case(api_request_factory, make_user):
    staff = make_user(username="staff", email="staff@example.com", is_staff=True)
    non_staff = make_user(username="nonstaff", email="nonstaff@example.com", is_staff=False)
    Order.objects.create(user=staff)
    Order.objects.create(user=non_staff)

    staff_req = api_request_factory.get("/api/orders/")
    force_authenticate(staff_req, user=staff)
    staff_view = OrderViewSet.as_view({"get": "list"})
    staff_resp = staff_view(staff_req)

    assert staff_resp.status_code == status.HTTP_200_OK
    assert staff_resp.data["count"] >= 2

    non_staff_req = api_request_factory.get("/api/orders/")
    force_authenticate(non_staff_req, user=non_staff)
    non_staff_view = OrderViewSet.as_view({"get": "list"})
    non_staff_resp = non_staff_view(non_staff_req)

    assert non_staff_resp.status_code == status.HTTP_200_OK
    assert non_staff_resp.data["count"] == 1
