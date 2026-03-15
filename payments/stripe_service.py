from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings


def _to_cents(amount: Decimal) -> int:
    return int((amount * Decimal("100")).quantize(Decimal("1")))


@dataclass(frozen=True)
class CheckoutSessionResult:
    session_id: str
    url: str
    payment_intent_id: str | None


class StripeService:
    def __init__(self):
        if not getattr(settings, "STRIPE_SECRET_KEY", ""):
            raise ValueError("STRIPE_SECRET_KEY is not configured")

        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        self._stripe = stripe

    def create_checkout_session(
        self,
        *,
        order_id: int,
        line_items: list[dict],
        success_url: str,
        cancel_url: str,
    ) -> CheckoutSessionResult:
        session = self._stripe.checkout.Session.create(
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=line_items,
            client_reference_id=str(order_id),
            metadata={"order_id": str(order_id)},
        )
        return CheckoutSessionResult(
            session_id=session["id"],
            url=session.get("url", ""),
            payment_intent_id=session.get("payment_intent"),
        )

    def construct_webhook_event(self, *, payload: bytes, signature: str):
        if not getattr(settings, "STRIPE_WEBHOOK_SECRET", ""):
            raise ValueError("STRIPE_WEBHOOK_SECRET is not configured")
        return self._stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

    def refund_payment_intent(self, *, payment_intent_id: str, amount: Decimal | None):
        params = {"payment_intent": payment_intent_id}
        if amount is not None:
            params["amount"] = _to_cents(amount)
        return self._stripe.Refund.create(**params)
