from decimal import Decimal

from rest_framework import serializers


class CreateCheckoutSessionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class RefundSerializer(serializers.Serializer):
    transaction_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

