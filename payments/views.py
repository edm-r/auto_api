from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from .invoice_pdf import render_invoice_pdf
from .models import Invoice, PaymentRefund, PaymentTransaction, StripeWebhookEvent
from .serializers import CreateCheckoutSessionSerializer, RefundSerializer
from .stripe_service import StripeService


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, pk=serializer.validated_data["order_id"])
        if not request.user.is_staff and order.user_id != request.user.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        currency = getattr(settings, "STRIPE_CURRENCY", "usd")

        # Build line items from order items
        order_items = order.items.select_related("product").all()
        if not order_items:
            return Response({"detail": "Order has no items."}, status=status.HTTP_400_BAD_REQUEST)

        line_items = []
        invalid_items = []
        for item in order_items:
            unit_amount = int((item.unit_price * Decimal("100")).quantize(Decimal("1")))
            if unit_amount <= 0:
                invalid_items.append(
                    {
                        "order_item_id": item.id,
                        "product_id": item.product_id,
                        "product_name": getattr(item.product, "name", ""),
                        "unit_price": str(item.unit_price),
                    }
                )
                continue
            line_items.append(
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": unit_amount,
                        "product_data": {"name": item.product.name},
                    },
                    "quantity": item.quantity,
                }
            )

        if invalid_items:
            return Response(
                {
                    "detail": "Some items have an invalid unit price for Stripe.",
                    "invalid_items": invalid_items,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = StripeService()
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            session = service.create_checkout_session(
                order_id=order.id,
                line_items=line_items,
                success_url=serializer.validated_data["success_url"],
                cancel_url=serializer.validated_data["cancel_url"],
            )
        except Exception as exc:
            # Best-effort: treat Stripe errors as client errors, everything else as upstream failure.
            try:
                import stripe  # type: ignore

                if isinstance(exc, stripe.error.StripeError):
                    detail = getattr(exc, "user_message", None) or str(exc) or "Stripe error."
                    return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                pass
            return Response(
                {"detail": "Failed to create Stripe checkout session."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not session.url:
            return Response(
                {"detail": "Stripe did not return a checkout URL."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        txn = PaymentTransaction.objects.create(
            order=order,
            user=order.user,
            stripe_checkout_session_id=session.session_id,
            stripe_payment_intent_id=session.payment_intent_id or "",
            amount=order.total,
            currency=currency,
            status=PaymentTransaction.Status.PENDING,
        )

        return Response(
            {"checkout_url": session.url, "session_id": session.session_id, "transaction_id": txn.id},
            status=status.HTTP_201_CREATED,
        )


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.headers.get("Stripe-Signature", "")

        try:
            service = StripeService()
            event = service.construct_webhook_event(payload=payload, signature=sig_header)
        except Exception:
            return Response({"detail": "Invalid webhook signature."}, status=status.HTTP_400_BAD_REQUEST)

        event_id = event["id"]
        event_type = event["type"]
        _event_obj, created = StripeWebhookEvent.objects.get_or_create(
            event_id=event_id,
            defaults={"event_type": event_type},
        )
        if not created:
            return Response({"received": True, "duplicate": True}, status=status.HTTP_200_OK)

        data_obj = event["data"]["object"]

        if event_type == "checkout.session.completed":
            session_id = data_obj["id"]
            payment_intent = data_obj.get("payment_intent", "") or ""
            customer_id = data_obj.get("customer", "") or ""
            txn = PaymentTransaction.objects.filter(stripe_checkout_session_id=session_id).select_related("order", "user").first()
            if txn is None:
                return Response({"received": True}, status=status.HTTP_200_OK)
            txn.stripe_payment_intent_id = payment_intent
            txn.stripe_customer_id = customer_id
            txn.status = PaymentTransaction.Status.SUCCEEDED
            txn.save(update_fields=["stripe_payment_intent_id", "stripe_customer_id", "status", "updated_at"])

            order = txn.order
            order.status = Order.Status.PAID
            order.save(update_fields=["status", "updated_at"])

            if not hasattr(txn, "invoice"):
                pdf = render_invoice_pdf(
                    transaction_id=txn.id,
                    customer=txn.user.username,
                    amount=str(txn.amount),
                    currency=txn.currency,
                    date=timezone.now().date().isoformat(),
                )
                Invoice.objects.create(transaction=txn, pdf=pdf)

        elif event_type == "payment_intent.payment_failed":
            payment_intent_id = data_obj["id"]
            txn = PaymentTransaction.objects.filter(stripe_payment_intent_id=payment_intent_id).select_related("order").first()
            if txn is None:
                return Response({"received": True}, status=status.HTTP_200_OK)
            txn.status = PaymentTransaction.Status.FAILED
            txn.save(update_fields=["status", "updated_at"])
            order = txn.order
            order.status = Order.Status.PAYMENT_FAILED
            order.save(update_fields=["status", "updated_at"])

        elif event_type == "payment_intent.succeeded":
            payment_intent_id = data_obj["id"]
            txn = PaymentTransaction.objects.filter(stripe_payment_intent_id=payment_intent_id).select_related("order").first()
            if txn is None:
                return Response({"received": True}, status=status.HTTP_200_OK)
            txn.status = PaymentTransaction.Status.SUCCEEDED
            txn.save(update_fields=["status", "updated_at"])
            order = txn.order
            order.status = Order.Status.PAID
            order.save(update_fields=["status", "updated_at"])

        return Response({"received": True}, status=status.HTTP_200_OK)


class RefundView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        txn = get_object_or_404(PaymentTransaction, pk=serializer.validated_data["transaction_id"])
        amount = serializer.validated_data.get("amount")

        if not txn.stripe_payment_intent_id:
            return Response({"detail": "Transaction has no payment_intent."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = StripeService()
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        refund = service.refund_payment_intent(payment_intent_id=txn.stripe_payment_intent_id, amount=amount)

        PaymentRefund.objects.create(
            transaction=txn,
            stripe_refund_id=refund["id"],
            amount=amount if amount is not None else txn.amount,
            status=refund.get("status", ""),
        )

        # If refund is full, mark refunded
        if amount is None or amount >= txn.amount:
            txn.status = PaymentTransaction.Status.REFUNDED
            txn.save(update_fields=["status", "updated_at"])
            order = txn.order
            order.status = Order.Status.REFUNDED
            order.save(update_fields=["status", "updated_at"])

        return Response({"refund_id": refund["id"]}, status=status.HTTP_200_OK)


class InvoiceDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, transaction_id: int):
        txn = get_object_or_404(PaymentTransaction, pk=transaction_id)
        if not request.user.is_staff and txn.user_id != request.user.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        invoice = get_object_or_404(Invoice, transaction=txn)
        response = HttpResponse(invoice.pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice-{txn.id}.pdf"'
        return response
