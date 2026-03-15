from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from orders.models import Order, OrderItem
from payments.models import Invoice, PaymentTransaction
from payments.views import (
    CreateCheckoutSessionView,
    InvoiceDownloadView,
    RefundView,
    StripeWebhookView,
)
from products.models import Brand, Category, Product


@pytest.fixture
def order_with_item(db, make_user):
    user = make_user(username="payer", email="payer@example.com", is_staff=False)
    category = Category.objects.create(name="PayCat")
    brand = Brand.objects.create(name="PayBrand")
    product = Product.objects.create(
        name="Pay Product",
        sku="PAY-001",
        description="Pay product",
        category=category,
        brand=brand,
        price=Decimal("12.34"),
        stock_quantity=100,
    )
    order = Order.objects.create(
        user=user,
        subtotal=Decimal("12.34"),
        tax=Decimal("0.00"),
        shipping_cost=Decimal("0.00"),
        total=Decimal("12.34"),
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=Decimal("12.34"),
        total_price=Decimal("12.34"),
    )
    return user, order


@pytest.mark.django_db
def test_create_session_success(api_request_factory, settings, mocker, order_with_item):
    settings.STRIPE_SECRET_KEY = "sk_test_123"
    settings.STRIPE_WEBHOOK_SECRET = "whsec_123"
    settings.STRIPE_CURRENCY = "usd"

    user, order = order_with_item

    create_mock = mocker.patch("stripe.checkout.Session.create")
    create_mock.return_value = {"id": "cs_test_1", "url": "https://checkout.test/cs_test_1", "payment_intent": "pi_1"}

    request = api_request_factory.post(
        "/api/payments/create-session/",
        {"order_id": order.id, "success_url": "https://example.com/success", "cancel_url": "https://example.com/cancel"},
        format="json",
    )
    force_authenticate(request, user=user)
    response = CreateCheckoutSessionView.as_view()(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["checkout_url"] == "https://checkout.test/cs_test_1"
    assert response.data["session_id"] == "cs_test_1"
    assert PaymentTransaction.objects.filter(order=order, stripe_checkout_session_id="cs_test_1").exists() is True


@pytest.mark.django_db
def test_webhook_checkout_completed_success(api_request_factory, settings, mocker, order_with_item):
    settings.STRIPE_SECRET_KEY = "sk_test_123"
    settings.STRIPE_WEBHOOK_SECRET = "whsec_123"

    user, order = order_with_item
    txn = PaymentTransaction.objects.create(
        order=order,
        user=user,
        stripe_checkout_session_id="cs_test_1",
        stripe_payment_intent_id="",
        amount=order.total,
        currency="usd",
        status=PaymentTransaction.Status.PENDING,
    )

    mocker.patch("stripe.Webhook.construct_event").return_value = {
        "id": "evt_1",
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_1", "payment_intent": "pi_1", "customer": "cus_1"}},
    }

    request = api_request_factory.post("/api/payments/webhook/", b"{}", content_type="application/json", HTTP_STRIPE_SIGNATURE="sig")
    response = StripeWebhookView.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    txn.refresh_from_db()
    order.refresh_from_db()
    assert txn.status == PaymentTransaction.Status.SUCCEEDED
    assert txn.stripe_payment_intent_id == "pi_1"
    assert order.status == Order.Status.PAID
    assert Invoice.objects.filter(transaction=txn).exists() is True


@pytest.mark.django_db
def test_refund_success(api_request_factory, settings, mocker, make_user, order_with_item):
    settings.STRIPE_SECRET_KEY = "sk_test_123"

    staff = make_user(username="staff", email="staff@example.com", is_staff=True)
    user, order = order_with_item
    txn = PaymentTransaction.objects.create(
        order=order,
        user=user,
        stripe_checkout_session_id="cs_test_1",
        stripe_payment_intent_id="pi_1",
        amount=Decimal("12.34"),
        currency="usd",
        status=PaymentTransaction.Status.SUCCEEDED,
    )

    mocker.patch("stripe.Refund.create").return_value = {"id": "re_1", "status": "succeeded"}

    request = api_request_factory.post("/api/payments/refund/", {"transaction_id": txn.id}, format="json")
    force_authenticate(request, user=staff)
    response = RefundView.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["refund_id"] == "re_1"
    txn.refresh_from_db()
    order.refresh_from_db()
    assert txn.status == PaymentTransaction.Status.REFUNDED
    assert order.status == Order.Status.REFUNDED


@pytest.mark.django_db
def test_invoice_download_success(api_request_factory, settings, make_user, order_with_item):
    settings.STRIPE_SECRET_KEY = "sk_test_123"

    user, order = order_with_item
    txn = PaymentTransaction.objects.create(
        order=order,
        user=user,
        stripe_checkout_session_id="cs_test_1",
        stripe_payment_intent_id="pi_1",
        amount=order.total,
        currency="usd",
        status=PaymentTransaction.Status.SUCCEEDED,
    )
    Invoice.objects.create(transaction=txn, pdf=b"%PDF-1.4 test")

    request = api_request_factory.get(f"/api/payments/invoice/{txn.id}/")
    force_authenticate(request, user=user)
    response = InvoiceDownloadView.as_view()(request, transaction_id=txn.id)

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")

