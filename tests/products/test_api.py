"""
Tests unitaires pour l'API Produits
Couvre les modèles, les sérialiseurs et les endpoints
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Category, Brand, CarModel, Product, ProductImage, ProductVariant
from products.serializers import (
    CategorySerializer, BrandSerializer, CarModelSerializer,
    ProductDetailSerializer, ProductVariantSerializer
)


# ============================================================================
# Tests des Modèles
# ============================================================================

class CategoryModelTest(TestCase):
    """Tests du modèle Category"""

    def setUp(self):
        """Crée les données de test"""
        self.category = Category.objects.create(
            name="Moteur",
            description="Pièces détachées du moteur"
        )

    def test_category_creation(self):
        """Test la création d'une catégorie"""
        self.assertEqual(self.category.name, "Moteur")
        self.assertTrue(self.category.is_active)
        self.assertIsNotNone(self.category.slug)

    def test_category_slug_generation(self):
        """Test la génération automatique du slug"""
        self.assertEqual(self.category.slug, "moteur")

    def test_category_string_representation(self):
        """Test la représentation string"""
        self.assertEqual(str(self.category), "Moteur")


class BrandModelTest(TestCase):
    """Tests du modèle Brand"""

    def setUp(self):
        """Crée les données de test"""
        self.brand = Brand.objects.create(
            name="Bosch",
            country="Germany",
            website="https://www.bosch.com"
        )

    def test_brand_creation(self):
        """Test la création d'une marque"""
        self.assertEqual(self.brand.name, "Bosch")
        self.assertEqual(self.brand.country, "Germany")

    def test_brand_slug_generation(self):
        """Test la génération du slug"""
        self.assertEqual(self.brand.slug, "bosch")

    def test_brand_uniqueness(self):
        """Test l'unicité du nom"""
        with self.assertRaises(Exception):
            Brand.objects.create(name="Bosch")


class CarModelModelTest(TestCase):
    """Tests du modèle CarModel"""

    def setUp(self):
        """Crée les données de test"""
        self.brand = Brand.objects.create(name="Peugeot")
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="308",
            year_start=2013,
            year_end=2021,
            body_type="hatchback"
        )

    def test_car_model_creation(self):
        """Test la création d'un modèle de voiture"""
        self.assertEqual(self.car_model.name, "308")
        self.assertEqual(self.car_model.year_start, 2013)

    def test_car_model_string_representation(self):
        """Test la représentation string"""
        self.assertIn("Peugeot", str(self.car_model))
        self.assertIn("308", str(self.car_model))

    def test_car_model_year_validation(self):
        """Test que les années ont du sens"""
        self.assertLess(self.car_model.year_start, self.car_model.year_end)


class ProductModelTest(TestCase):
    """Tests du modèle Product"""

    def setUp(self):
        """Crée les données de test"""
        self.category = Category.objects.create(name="Freins")
        self.brand = Brand.objects.create(name="Bosch")
        self.product = Product.objects.create(
            name="Plaquettes de freins",
            sku="BRAKE-001",
            description="Plaquettes de freins haute qualité",
            category=self.category,
            brand=self.brand,
            price=49.99,
            cost=25.00,
            stock_quantity=100
        )

    def test_product_creation(self):
        """Test la création d'un produit"""
        self.assertEqual(self.product.name, "Plaquettes de freins")
        self.assertEqual(self.product.sku, "BRAKE-001")

    def test_product_is_in_stock(self):
        """Test la propriété is_in_stock"""
        self.assertTrue(self.product.is_in_stock)
        self.product.stock_quantity = 0
        self.assertFalse(self.product.is_in_stock)

    def test_product_discount_percentage(self):
        """Test le calcul de marge"""
        expected = round(((49.99 - 25.00) / 49.99) * 100, 2)
        self.assertEqual(self.product.discount_percentage, expected)

    def test_product_low_stock_alert(self):
        """Test l'alerte stock bas"""
        self.product.stock_quantity = 5
        self.product.low_stock_alert = 10
        self.assertTrue(self.product.is_low_stock)


class ProductImageModelTest(TestCase):
    """Tests du modèle ProductImage"""

    def setUp(self):
        """Crée les données de test"""
        self.category = Category.objects.create(name="Moteur")
        self.product = Product.objects.create(
            name="Filtre à air",
            sku="FILTER-001",
            description="Filtre à air moteur",
            category=self.category,
            price=15.99
        )

    def test_primary_image_uniqueness(self):
        """Test qu'une seule image primaire par produit"""
        image1 = ProductImage.objects.create(
            product=self.product,
            image="test1.jpg",
            is_primary=True
        )
        image2 = ProductImage.objects.create(
            product=self.product,
            image="test2.jpg",
            is_primary=True
        )
        
        # Actualiser image1 depuis la base de données
        image1.refresh_from_db()
        self.assertFalse(image1.is_primary)
        self.assertTrue(image2.is_primary)


class ProductVariantModelTest(TestCase):
    """Tests du modèle ProductVariant"""

    def setUp(self):
        """Crée les données de test"""
        self.category = Category.objects.create(name="Freins")
        self.product = Product.objects.create(
            name="Plaquettes",
            sku="BRAKE-001",
            description="Plaquettes",
            category=self.category,
            price=49.99
        )

    def test_variant_creation(self):
        """Test la création d'une variante"""
        variant = ProductVariant.objects.create(
            product=self.product,
            name="Essieu avant",
            sku="BRAKE-001-FRONT",
            attribute_name="position",
            attribute_value="avant",
            stock_quantity=50
        )
        self.assertEqual(variant.name, "Essieu avant")
        self.assertTrue(variant.is_in_stock)

    def test_variant_final_price(self):
        """Test le calcul du prix final"""
        variant = ProductVariant.objects.create(
            product=self.product,
            name="Version premium",
            sku="BRAKE-001-PREMIUM",
            attribute_name="version",
            attribute_value="premium",
            price_modifier=10.00,
            stock_quantity=20
        )
        expected_price = self.product.price + variant.price_modifier
        self.assertEqual(variant.final_price, expected_price)


# ============================================================================
# Tests des Endpoints API
# ============================================================================

class CategoryAPITest(APITestCase):
    """Tests des endpoints de catégories"""

    def setUp(self):
        """Crée les données de test"""
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.category = Category.objects.create(
            name="Moteur",
            description="Pièces du moteur"
        )

    def test_list_categories(self):
        """Test la liste des catégories"""
        response = self.client.get('/api/products/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_category(self):
        """Test la récupération d'une catégorie"""
        response = self.client.get(f'/api/products/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Moteur")

    def test_create_category_as_admin(self):
        """Test la création de catégorie par un admin"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Suspension',
            'description': 'Pièces de suspension'
        }
        response = self.client.post('/api/products/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_as_anonymous(self):
        """Test que les anonymes ne peuvent pas créer"""
        data = {'name': 'Freins'}
        response = self.client.post('/api/products/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BrandAPITest(APITestCase):
    """Tests des endpoints de marques"""

    def setUp(self):
        """Crée les données de test"""
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.brand = Brand.objects.create(
            name="Bosch",
            country="Germany"
        )

    def test_list_brands(self):
        """Test la liste des marques"""
        response = self.client.get('/api/products/brands/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_brand(self):
        """Test la récupération d'une marque"""
        response = self.client.get(f'/api/products/brands/{self.brand.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Bosch")

    def test_search_brands(self):
        """Test la recherche de marques"""
        Brand.objects.create(name="Michelin", country="France")
        response = self.client.get('/api/products/brands/?search=Michelin')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(b['name'] == 'Michelin' for b in response.data['results']))


class CarModelAPITest(APITestCase):
    """Tests des endpoints de modèles de voitures"""

    def setUp(self):
        """Crée les données de test"""
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.brand = Brand.objects.create(name="Peugeot")
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name="308",
            year_start=2013,
            year_end=2021,
            body_type="hatchback"
        )

    def test_list_car_models(self):
        """Test la liste des modèles"""
        response = self.client.get('/api/products/car-models/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_brand(self):
        """Test le filtrage par marque"""
        response = self.client.get(f'/api/products/car-models/?brand={self.brand.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_body_type(self):
        """Test le filtrage par type de carrosserie"""
        response = self.client.get('/api/products/car-models/?body_type=hatchback')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductAPITest(APITestCase):
    """Tests des endpoints de produits"""

    def setUp(self):
        """Crée les données de test"""
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.category = Category.objects.create(name="Freins")
        self.brand = Brand.objects.create(name="Bosch")
        self.product = Product.objects.create(
            name="Plaquettes",
            sku="BRAKE-001",
            description="Plaquettes de freins",
            category=self.category,
            brand=self.brand,
            price=49.99,
            cost=25.00,
            stock_quantity=100,
            created_by=self.user
        )

    def test_list_products(self):
        """Test la liste des produits"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product(self):
        """Test la récupération d'un produit"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Plaquettes")

    def test_filter_by_category(self):
        """Test le filtrage par catégorie"""
        response = self.client.get(f'/api/products/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_products(self):
        """Test la recherche de produits"""
        response = self.client.get('/api/products/?search=Plaquettes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_as_admin(self):
        """Test la création d'un produit"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Filtre à air',
            'sku': 'FILTER-001',
            'description': 'Filtre à air moteur',
            'category': self.category.id,
            'brand': self.brand.id,
            'price': 15.99,
            'stock_quantity': 50
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_duplicate_sku(self):
        """Test qu'on ne peut pas créer deux produits avec le même SKU"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Autre produit',
            'sku': 'BRAKE-001',  # Même SKU
            'description': 'Description',
            'category': self.category.id,
            'price': 20.00,
            'stock_quantity': 50
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_featured_products(self):
        """Test la liste des produits en vedette"""
        self.product.is_featured = True
        self.product.save()
        response = self.client.get('/api/products/featured/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_stock(self):
        """Test la mise à jour du stock"""
        self.client.force_authenticate(user=self.user)
        data = {'quantity': 200}
        response = self.client.post(f'/api/products/{self.product.id}/update_stock/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock_quantity'], 200)


class ProductVariantAPITest(APITestCase):
    """Tests des endpoints de variantes"""

    def setUp(self):
        """Crée les données de test"""
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.category = Category.objects.create(name="Freins")
        self.product = Product.objects.create(
            name="Plaquettes",
            sku="BRAKE-001",
            description="Plaquettes",
            category=self.category,
            price=49.99,
            created_by=self.user
        )

    def test_add_variant(self):
        """Test l'ajout d'une variante"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Front',
            'sku': 'BRAKE-001-F',
            'attribute_name': 'other',
            'attribute_value': 'front',
            'stock_quantity': 50
        }
        response = self.client.post(f'/api/products/{self.product.id}/variants/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_variant_edge_case(self):
        """Test ajout variante sur produit inactif (admin)"""
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])

        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Rear',
            'sku': 'BRAKE-001-R',
            'attribute_name': 'other',
            'attribute_value': 'rear',
            'stock_quantity': 25
        }
        response = self.client.post(f'/api/products/{self.product.id}/variants/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


if __name__ == '__main__':
    import unittest
    unittest.main()
