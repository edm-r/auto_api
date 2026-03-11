from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, CarModelViewSet,
    ProductViewSet, ProductImageViewSet, ProductVariantViewSet
)

# Créer le routeur
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'car-models', CarModelViewSet, basename='car-model')
router.register(r'', ProductViewSet, basename='product')
router.register(r'images', ProductImageViewSet, basename='product-image')
router.register(r'variants', ProductVariantViewSet, basename='product-variant')

urlpatterns = [
    path('', include(router.urls)),
]
