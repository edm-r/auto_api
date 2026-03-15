from django.contrib import admin

from .models import Invoice, PaymentRefund, PaymentTransaction, StripeWebhookEvent


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "user", "status", "amount", "currency", "created_at"]
    list_filter = ["status", "currency"]
    search_fields = ["id", "stripe_checkout_session_id", "stripe_payment_intent_id", "user__username", "order__id"]


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction", "amount", "status", "created_at"]
    search_fields = ["id", "stripe_refund_id", "transaction__id"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction", "created_at"]
    search_fields = ["id", "transaction__id"]


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ["event_id", "event_type", "created_at"]
    search_fields = ["event_id", "event_type"]

