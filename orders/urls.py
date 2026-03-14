from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, CartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"cart/items", CartItemViewSet, basename="cart-item")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = router.urls

