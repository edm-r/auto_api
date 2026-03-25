from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ShipmentViewSet, ShippingAddressViewSet

app_name = "shipping"

router = DefaultRouter()
router.register(r"addresses", ShippingAddressViewSet, basename="shipping-address")
router.register(r"shipments", ShipmentViewSet, basename="shipment")

urlpatterns = [
    path("", include(router.urls)),
]
