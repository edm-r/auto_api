from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from customers.models import Address
from orders.models import Order
from shipping.models import Shipment
from shipping.views import ShipmentViewSet, ShippingAddressViewSet


@pytest.fixture
def user(db, make_user):
    return make_user(username="shipper", email="shipper@example.com", is_staff=False)


@pytest.fixture
def other_user(db, make_user):
    return make_user(username="other", email="other@example.com", is_staff=False)


@pytest.fixture
def staff(db, make_user):
    return make_user(username="staffship", email="staffship@example.com", is_staff=True)


@pytest.fixture
def order(db, user):
    return Order.objects.create(user=user, subtotal=Decimal("10.00"), tax=Decimal("1.00"), shipping_cost=Decimal("2.00"), total=Decimal("13.00"))


@pytest.mark.django_db
def test_addresses_create_and_list_success(api_request_factory, user):
    create_req = api_request_factory.post(
        "/api/shipping/addresses/",
        {
            "full_name": "John Doe",
            "phone_number": "+237600000000",
            "address_line": "Rue 1",
            "city": "Douala",
            "region": "LT",
            "postal_code": "0000",
            "country": "CM",
            "is_default": True,
        },
        format="json",
    )
    force_authenticate(create_req, user=user)
    create_view = ShippingAddressViewSet.as_view({"post": "create"})
    create_resp = create_view(create_req)

    assert create_resp.status_code == status.HTTP_201_CREATED
    assert create_resp.data["id"] is not None
    assert create_resp.data["is_default"] is True

    list_req = api_request_factory.get("/api/shipping/addresses/")
    force_authenticate(list_req, user=user)
    list_view = ShippingAddressViewSet.as_view({"get": "list"})
    list_resp = list_view(list_req)

    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.data["count"] == 1
    assert list_resp.data["results"][0]["city"] == "Douala"


@pytest.mark.django_db
def test_addresses_isolation_success(api_request_factory, user, other_user):
    Address.objects.create(
        user=user,
        full_name="User One",
        phone_number="",
        address_line="Addr 1",
        city="Yaounde",
        region="",
        postal_code="",
        country="CM",
        is_default=True,
    )

    other_req = api_request_factory.get("/api/shipping/addresses/")
    force_authenticate(other_req, user=other_user)
    view = ShippingAddressViewSet.as_view({"get": "list"})
    other_resp = view(other_req)

    assert other_resp.status_code == status.HTTP_200_OK
    assert other_resp.data["count"] == 0


@pytest.mark.django_db
def test_shipments_staff_create_and_user_list_success(api_request_factory, staff, user, order):
    address = Address.objects.create(
        user=user,
        full_name="Buyer",
        phone_number="",
        address_line="Addr",
        city="Douala",
        region="",
        postal_code="",
        country="CM",
        is_default=True,
    )

    create_req = api_request_factory.post(
        "/api/shipping/shipments/",
        {"order_id": order.id, "address_id": address.id, "carrier": "DHL", "tracking_number": "TRK123"},
        format="json",
    )
    force_authenticate(create_req, user=staff)
    create_view = ShipmentViewSet.as_view({"post": "create"})
    create_resp = create_view(create_req)

    assert create_resp.status_code == status.HTTP_201_CREATED
    assert create_resp.data["order_id"] == order.id
    assert create_resp.data["carrier"] == "DHL"

    list_req = api_request_factory.get("/api/shipping/shipments/")
    force_authenticate(list_req, user=user)
    list_view = ShipmentViewSet.as_view({"get": "list"})
    list_resp = list_view(list_req)

    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.data["count"] == 1
    assert list_resp.data["results"][0]["tracking_number"] == "TRK123"


@pytest.mark.django_db
def test_shipments_mark_shipped_updates_order_success(api_request_factory, staff, user, order):
    address = Address.objects.create(
        user=user,
        full_name="Buyer",
        phone_number="",
        address_line="Addr",
        city="Douala",
        region="",
        postal_code="",
        country="CM",
        is_default=True,
    )
    shipment = Shipment.objects.create(order=order, address=address, carrier="", tracking_number="")

    req = api_request_factory.post("/api/shipping/shipments/1/mark_shipped/", {"carrier": "UPS", "tracking_number": "X1"}, format="json")
    force_authenticate(req, user=staff)
    view = ShipmentViewSet.as_view({"post": "mark_shipped"})
    resp = view(req, pk=shipment.id)

    assert resp.status_code == status.HTTP_200_OK
    shipment.refresh_from_db()
    order.refresh_from_db()
    assert shipment.status == "shipped"
    assert shipment.shipped_at is not None
    assert order.status == "shipped"
