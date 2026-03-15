from django.urls import path

from .views import CreateCheckoutSessionView, InvoiceDownloadView, RefundView, StripeWebhookView

urlpatterns = [
    path("payments/create-session/", CreateCheckoutSessionView.as_view(), name="payments_create_session"),
    path("payments/webhook/", StripeWebhookView.as_view(), name="payments_webhook"),
    path("payments/refund/", RefundView.as_view(), name="payments_refund"),
    path("payments/invoice/<int:transaction_id>/", InvoiceDownloadView.as_view(), name="payments_invoice"),
]

