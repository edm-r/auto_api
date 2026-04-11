from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, CarModelViewSet,
    ProductViewSet, ProductImageViewSet, ProductVariantViewSet,
    WarehouseViewSet, InventoryViewSet, StockMovementViewSet
)

# Créer le routeur
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'car-models', CarModelViewSet, basename='car-model')
router.register(r'images', ProductImageViewSet, basename='product-image')
router.register(r'variants', ProductVariantViewSet, basename='product-variant')
<<<<<<< HEAD
=======
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')
>>>>>>> 44970c59e35949e73642dc21e2a0b10db4a58dbb
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
