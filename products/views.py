from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F

from .models import Category, Brand, CarModel, Product, ProductImage, ProductVariant
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    BrandSerializer,
    CarModelSerializer, CarModelSimpleSerializer,
    ProductDetailSerializer, ProductSimpleSerializer, ProductCreateUpdateSerializer,
    ProductImageSerializer, ProductImageDetailSerializer,
    ProductVariantSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les catégories de produits
    
    Endpoints:
    - GET /api/products/categories/ - Lister toutes les catégories
    - POST /api/products/categories/ - Créer une catégorie (admin)
    - GET /api/products/categories/{id}/ - Détails d'une catégorie
    - PUT /api/products/categories/{id}/ - Modifier (admin)
    - DELETE /api/products/categories/{id}/ - Supprimer (admin)
    """
    queryset = Category.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Utilise différentes sérialiseurs selon l'action"""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    def get_permissions(self):
        """Permissions: lecture pour tous, écriture pour admins"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Liste tous les produits d'une catégorie"""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        serializer = ProductSimpleSerializer(products, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les marques
    
    Endpoints:
    - GET /api/products/brands/ - Lister toutes les marques
    - POST /api/products/brands/ - Créer une marque (admin)
    - GET /api/products/brands/{id}/ - Détails d'une marque
    - PUT /api/products/brands/{id}/ - Modifier (admin)
    - DELETE /api/products/brands/{id}/ - Supprimer (admin)
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        """Permissions: lecture pour tous, écriture pour admins"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def car_models(self, request, pk=None):
        """Liste tous les modèles de voitures d'une marque"""
        brand = self.get_object()
        models = brand.car_models.filter(is_active=True)
        serializer = CarModelSimpleSerializer(models, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Liste tous les produits d'une marque"""
        brand = self.get_object()
        products = brand.products.filter(is_active=True)
        serializer = ProductSimpleSerializer(products, many=True)
        return Response(serializer.data)


class CarModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les modèles de voitures
    
    Endpoints:
    - GET /api/products/car-models/ - Lister tous les modèles
    - POST /api/products/car-models/ - Créer un modèle (admin)
    - GET /api/products/car-models/{id}/ - Détails du modèle
    - PUT /api/products/car-models/{id}/ - Modifier (admin)
    - DELETE /api/products/car-models/{id}/ - Supprimer (admin)
    """
    serializer_class = CarModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'body_type', 'is_active']
    search_fields = ['name', 'brand__name']
    ordering_fields = ['year_start', 'name', 'created_at']
    ordering = ['-year_start', 'name']

    def get_queryset(self):
        """Filtre par défaut: modèles actifs uniquement"""
        queryset = CarModel.objects.all()
        is_active = self.request.query_params.get('is_active', 'true')
        if is_active.lower() != 'all':
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_permissions(self):
        """Permissions: lecture pour tous, écriture pour admins"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Liste tous les produits compatibles avec ce modèle"""
        car_model = self.get_object()
        products = car_model.products.filter(is_active=True)
        serializer = ProductSimpleSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les produits
    
    Endpoints:
    - GET /api/products/ - Lister tous les produits
    - POST /api/products/ - Créer un produit (admin)
    - GET /api/products/{id}/ - Détails du produit
    - PUT /api/products/{id}/ - Modifier un produit (admin)
    - PATCH /api/products/{id}/ - Modification partielle (admin)
    - DELETE /api/products/{id}/ - Supprimer (admin)
    
    Filtrage:
    - ?category=id - Par catégorie
    - ?brand=id - Par marque
    - ?is_active=true/false - Actifs/inactifs
    - ?is_featured=true - Produits en vedette
    - ?search=terme - Recherche textuelle
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'sku', 'category__name']
    ordering_fields = ['price', 'stock_quantity', 'rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filtre par défaut: produits actifs (sauf staff)"""
        queryset = Product.objects.prefetch_related(
            'images', 'variants', 'compatible_car_models'
        ).select_related('category', 'brand', 'created_by')
        
        # Filtre pour ignorer les produits inactifs par défaut
        # Important: les admins doivent pouvoir modifier un produit inactif (ex: ajouter une variante).
        default_is_active = 'all' if getattr(self.request.user, 'is_staff', False) else 'true'
        is_active = self.request.query_params.get('is_active', default_is_active).lower()
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset

    def get_serializer_class(self):
        """Utilise différents sérialiseurs selon l'action"""
        if self.action == 'list':
            return ProductSimpleSerializer
        elif self.action in ['create', 'partial_update', 'update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        """Permissions: lecture pour tous, écriture pour admins"""
        read_actions = {'list', 'retrieve', 'featured', 'low_stock', 'out_of_stock'}
        if self.action in read_actions:
            permission_classes = [AllowAny]
        elif self.action in {'images', 'variants'} and self.request.method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Ajoute l'utilisateur au créateur du produit"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def images(self, request, pk=None):
        """Gère les images du produit"""
        product = self.get_object()
        
        if request.method == 'GET':
            images = product.images.all()
            serializer = ProductImageDetailSerializer(images, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if not request.user.is_staff:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data.copy()
            data['product'] = product.id
            serializer = ProductImageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def variants(self, request, pk=None):
        """Gère les variantes du produit"""
        product = self.get_object()
        
        if request.method == 'GET':
            variants = product.variants.all()
            serializer = ProductVariantSerializer(variants, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if not request.user.is_staff:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data.copy()
            data['product'] = product.id
            serializer = ProductVariantSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Liste les produits en vedette"""
        products = self.get_queryset().filter(is_featured=True)
        serializer = ProductSimpleSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Liste les produits en rupture imminente"""
        products = self.get_queryset().filter(stock_quantity__lte=F('low_stock_alert'))
        serializer = ProductSimpleSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Liste les produits rupture de stock"""
        products = self.get_queryset().filter(stock_quantity=0)
        serializer = ProductSimpleSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Met à jour le stock du produit"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        product = self.get_object()
        quantity = request.data.get('quantity')
        
        if quantity is None:
            return Response(
                {'error': 'quantity field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            product.stock_quantity = quantity
            product.save()
            return Response({
                'id': product.id,
                'stock_quantity': product.stock_quantity
            })
        except ValueError:
            return Response(
                {'error': 'quantity must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les images des produits
    """
    serializer_class = ProductImageSerializer
    permission_classes = [AllowAny]  # GET pour tous, POST/DELETE pour admins

    def get_queryset(self):
        """Récupère les images, filtrable par produit"""
        queryset = ProductImage.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def get_permissions(self):
        """Permissions par action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les variantes des produits
    """
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'attribute_name', 'is_active']
    search_fields = ['name', 'sku']

    def get_queryset(self):
        """Récupère les variantes"""
        queryset = ProductVariant.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def get_permissions(self):
        """Permissions par action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
