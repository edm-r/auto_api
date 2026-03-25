from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from customers.models import UserProfile, VehiclePreference, WishList
from customers.views import AddressViewSet, OrderHistoryViewSet, ProfileMeView, VehiclePreferenceViewSet, WishListViewSet
from orders.models import Order
from products.models import Brand, Category, Product


@pytest.fixture
def user(db, make_user):
    return make_user(username="customer", email="customer@example.com", is_staff=False)


@pytest.fixture
def other_user(db, make_user):
    return make_user(username="othercust", email="othercust@example.com", is_staff=False)


@pytest.fixture
def product(db):
    category = Category.objects.create(name="WishCat")
    brand = Brand.objects.create(name="WishBrand")
    return Product.objects.create(
        name="Wishlist Product",
        sku="WISH-001",
        description="Wishlist product",
        category=category,
        brand=brand,
        price=Decimal("10.00"),
        stock_quantity=10,
    )


@pytest.mark.django_db
def test_profile_auto_created_on_user_create_success(user):
    assert UserProfile.objects.filter(user=user).exists() is True
    assert WishList.objects.filter(user=user).exists() is True


@pytest.mark.django_db
def test_profile_me_get_and_put_success(api_request_factory, user):
    get_req = api_request_factory.get("/api/profile/me/")
    force_authenticate(get_req, user=user)
    get_resp = ProfileMeView.as_view()(get_req)
    assert get_resp.status_code == status.HTTP_200_OK
    assert "phone_number" in get_resp.data

    put_req = api_request_factory.put("/api/profile/me/", {"phone_number": "+237600000001"}, format="json")
    force_authenticate(put_req, user=user)
    put_resp = ProfileMeView.as_view()(put_req)
    assert put_resp.status_code == status.HTTP_200_OK
    assert put_resp.data["phone_number"] == "+237600000001"


@pytest.mark.django_db
def test_addresses_default_unique_success(api_request_factory, user):
    create_view = AddressViewSet.as_view({"post": "create"})
    list_view = AddressViewSet.as_view({"get": "list"})

    req1 = api_request_factory.post(
        "/api/profile/addresses/",
        {
            "full_name": "A",
            "phone_number": "",
            "address_line": "Addr 1",
            "city": "Douala",
            "region": "",
            "country": "CM",
            "postal_code": "",
            "is_default": True,
        },
        format="json",
    )
    force_authenticate(req1, user=user)
    resp1 = create_view(req1)
    assert resp1.status_code == status.HTTP_201_CREATED
    assert resp1.data["is_default"] is True

    req2 = api_request_factory.post(
        "/api/profile/addresses/",
        {
            "full_name": "B",
            "phone_number": "",
            "address_line": "Addr 2",
            "city": "Yaounde",
            "region": "",
            "country": "CM",
            "postal_code": "",
            "is_default": True,
        },
        format="json",
    )
    force_authenticate(req2, user=user)
    resp2 = create_view(req2)
    assert resp2.status_code == status.HTTP_201_CREATED

    list_req = api_request_factory.get("/api/profile/addresses/")
    force_authenticate(list_req, user=user)
    list_resp = list_view(list_req)
    assert list_resp.status_code == status.HTTP_200_OK
    defaults = [a for a in list_resp.data["results"] if a["is_default"]]
    assert len(defaults) == 1


@pytest.mark.django_db
def test_wishlist_add_and_remove_success(api_request_factory, user, product):
    list_view = WishListViewSet.as_view({"get": "list"})
    add_view = WishListViewSet.as_view({"post": "add"})
    remove_view = WishListViewSet.as_view({"post": "remove"})

    list_req = api_request_factory.get("/api/profile/wishlist/")
    force_authenticate(list_req, user=user)
    list_resp = list_view(list_req)
    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.data["product_ids"] == []

    add_req = api_request_factory.post("/api/profile/wishlist/add/", {"product_id": product.id}, format="json")
    force_authenticate(add_req, user=user)
    add_resp = add_view(add_req)
    assert add_resp.status_code == status.HTTP_200_OK
    assert product.id in add_resp.data["product_ids"]

    remove_req = api_request_factory.post("/api/profile/wishlist/remove/", {"product_id": product.id}, format="json")
    force_authenticate(remove_req, user=user)
    remove_resp = remove_view(remove_req)
    assert remove_resp.status_code == status.HTTP_200_OK
    assert remove_resp.data["product_ids"] == []


@pytest.mark.django_db
def test_vehicle_preferences_crud_success(api_request_factory, user):
    create_view = VehiclePreferenceViewSet.as_view({"post": "create"})
    list_view = VehiclePreferenceViewSet.as_view({"get": "list"})

    create_req = api_request_factory.post(
        "/api/profile/vehicles/",
        {"brand": "Toyota", "model": "Corolla", "year": 2012, "engine_type": "diesel"},
        format="json",
    )
    force_authenticate(create_req, user=user)
    create_resp = create_view(create_req)
    assert create_resp.status_code == status.HTTP_201_CREATED

    list_req = api_request_factory.get("/api/profile/vehicles/")
    force_authenticate(list_req, user=user)
    list_resp = list_view(list_req)
    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.data["count"] == 1

    assert VehiclePreference.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_order_history_isolated_success(api_request_factory, user, other_user):
    Order.objects.create(user=user, subtotal=Decimal("1.00"), tax=Decimal("0.00"), shipping_cost=Decimal("0.00"), total=Decimal("1.00"))
    Order.objects.create(user=other_user, subtotal=Decimal("2.00"), tax=Decimal("0.00"), shipping_cost=Decimal("0.00"), total=Decimal("2.00"))

    req = api_request_factory.get("/api/profile/orders/")
    force_authenticate(req, user=user)
    view = OrderHistoryViewSet.as_view({"get": "list"})
    resp = view(req)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["count"] == 1

