import pytest

from products.models import Brand, CarModel, Category, Product
from products.serializers import ProductCreateUpdateSerializer


@pytest.mark.django_db
def test_create_success(api_request_factory, make_user):
    user = make_user(username="prod-admin", email="prod-admin@example.com", is_staff=True)
    category = Category.objects.create(name="Filters")
    brand = Brand.objects.create(name="Bosch")
    car_model = CarModel.objects.create(brand=brand, name="308", year_start=2013)

    payload = {
        "name": "Air Filter",
        "description": "Engine air filter",
        "sku": "FILTER-UT-001",
        "category": category.id,
        "brand": brand.id,
        "compatible_car_models_ids": [car_model.id],
        "price": "15.99",
        "stock_quantity": 50,
    }
    request = api_request_factory.post("/api/products/", payload, format="json")
    request.user = user
    serializer = ProductCreateUpdateSerializer(data=payload, context={"request": request})

    is_valid = serializer.is_valid()

    assert is_valid is True
    product = serializer.save(created_by=user)
    assert isinstance(product, Product)
    assert product.created_by_id == user.id
    assert list(product.compatible_car_models.values_list("id", flat=True)) == [car_model.id]


@pytest.mark.django_db
def test_create_edge_case(api_request_factory, make_user):
    user = make_user(username="prod-admin-2", email="prod-admin-2@example.com", is_staff=True)
    category = Category.objects.create(name="Brakes")

    payload = {
        "name": "Brake Pads",
        "description": "Brake pads",
        "sku": "BRAKE-UT-001",
        "category": category.id,
        "price": "49.99",
        "stock_quantity": 10,
    }
    request = api_request_factory.post("/api/products/", payload, format="json")
    request.user = user
    serializer = ProductCreateUpdateSerializer(data=payload, context={"request": request})

    is_valid = serializer.is_valid()

    assert is_valid is True
    product = serializer.save()
    assert product.created_by_id == user.id
    assert product.compatible_car_models.count() == 0
