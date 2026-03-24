from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AddressViewSet, OrderHistoryViewSet, ProfileMeView, VehiclePreferenceViewSet, WishListViewSet


router = DefaultRouter()
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"wishlist", WishListViewSet, basename="wishlist")
router.register(r"vehicles", VehiclePreferenceViewSet, basename="vehicle-preference")
router.register(r"orders", OrderHistoryViewSet, basename="order-history")

urlpatterns = [
    path("me/", ProfileMeView.as_view(), name="profile-me"),
]
urlpatterns += router.urls

