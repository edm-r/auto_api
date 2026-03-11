#!/usr/bin/env python
"""
Script de test pour valider les endpoints de l'API Produits
Run: python test_products_endpoints.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
ADMIN_CREDS = {"username": "admin", "password": "adminpass123"}

# Couleurs pour l'affichage
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Statistiques des tests
tests_passed = 0
tests_failed = 0
tests_total = 0

def print_header(text):
    """Affiche un en-tête"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_test(name, status, response=None):
    """Affiche le résultat d'un test"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    
    if status:
        tests_passed += 1
        print(f"{GREEN}✓ PASS{RESET}: {name}")
    else:
        tests_failed += 1
        print(f"{RED}✗ FAIL{RESET}: {name}")
        if response:
            print(f"  Status: {response.status_code}")
            try:
                print(f"  Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"  Response: {response.text}")

def get_auth_token():
    """Récupère un token JWT pour l'authentification"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=ADMIN_CREDS
        )
        if response.status_code == 200:
            token = response.json().get('access')
            print(f"{GREEN}✓ Token obtenu{RESET}")
            return token
        else:
            print(f"{RED}✗ Impossible d'obtenir le token{RESET}")
            return None
    except Exception as e:
        print(f"{RED}✗ Erreur lors de la connexion: {e}{RESET}")
        return None

def make_request(method, endpoint, token=None, data=None):
    """Fait une requête HTTP"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return None
        
        return response
    except Exception as e:
        print(f"{RED}✗ Erreur de requête: {e}{RESET}")
        return None

# ============================================================================
# TESTS
# ============================================================================

def test_categories(token):
    """Test les endpoints de catégories"""
    print_header("TEST: CATÉGORIES")
    
    # Test: Lister les catégories
    response = make_request('GET', '/products/categories/')
    print_test("Lister les catégories", response and response.status_code == 200, response)
    
    # Test: Créer une catégorie
    category_data = {
        'name': f'Moteur Test {int(time.time())}',
        'description': 'Catégorie de test pour les pièces du moteur'
    }
    response = make_request('POST', '/products/categories/', token, category_data)
    print_test("Créer une catégorie (admin)", response and response.status_code == 201, response)
    
    if response and response.status_code == 201:
        category_id = response.json()['id']
        
        # Test: Récupérer une catégorie
        response = make_request('GET', f'/products/categories/{category_id}/')
        print_test("Récupérer une catégorie", response and response.status_code == 200, response)
        
        # Test: Modifier une catégorie
        update_data = {'description': 'Description mise à jour'}
        response = make_request('PUT', f'/products/categories/{category_id}/', token, update_data)
        print_test("Modifier une catégorie", response and response.status_code == 200, response)
        
        # Test: Supprimer une catégorie
        response = make_request('DELETE', f'/products/categories/{category_id}/', token)
        print_test("Supprimer une catégorie", response and response.status_code == 204, response)

def test_brands(token):
    """Test les endpoints de marques"""
    print_header("TEST: MARQUES")
    
    # Test: Lister les marques
    response = make_request('GET', '/products/brands/')
    print_test("Lister les marques", response and response.status_code == 200, response)
    
    # Test: Créer une marque
    brand_data = {
        'name': f'Bosch {int(time.time())}',
        'country': 'Germany',
        'description': 'Marque de test'
    }
    response = make_request('POST', '/products/brands/', token, brand_data)
    print_test("Créer une marque (admin)", response and response.status_code == 201, response)
    
    if response and response.status_code == 201:
        brand_id = response.json()['id']
        
        # Test: Récupérer une marque
        response = make_request('GET', f'/products/brands/{brand_id}/')
        print_test("Récupérer une marque", response and response.status_code == 200, response)

def test_car_models(token):
    """Test les endpoints de modèles de voitures"""
    print_header("TEST: MODÈLES DE VOITURES")
    
    # D'abord créer une marque
    brand_data = {
        'name': f'Peugeot {int(time.time())}',
        'country': 'France'
    }
    response = make_request('POST', '/products/brands/', token, brand_data)
    brand_id = response.json()['id'] if response and response.status_code == 201 else None
    
    if not brand_id:
        print(f"{RED}✗ Impossible de créer une marque pour les tests{RESET}")
        return
    
    # Test: Lister les modèles de voitures
    response = make_request('GET', '/products/car-models/')
    print_test("Lister les modèles de voitures", response and response.status_code == 200, response)
    
    # Test: Créer un modèle de voiture
    car_model_data = {
        'brand': brand_id,
        'name': f'308 {int(time.time())}',
        'year_start': 2013,
        'year_end': 2021,
        'body_type': 'hatchback'
    }
    response = make_request('POST', '/products/car-models/', token, car_model_data)
    print_test("Créer un modèle de voiture (admin)", response and response.status_code == 201, response)
    
    if response and response.status_code == 201:
        car_model_id = response.json()['id']
        
        # Test: Récupérer un modèle
        response = make_request('GET', f'/products/car-models/{car_model_id}/')
        print_test("Récupérer un modèle de voiture", response and response.status_code == 200, response)

def test_products(token):
    """Test les endpoints de produits"""
    print_header("TEST: PRODUITS")
    
    # Créer une catégorie et une marque
    category_data = {'name': f'Freins {int(time.time())}', 'description': 'Freins'}
    response = make_request('POST', '/products/categories/', token, category_data)
    category_id = response.json()['id'] if response and response.status_code == 201 else None
    
    brand_data = {'name': f'ATE {int(time.time())}', 'country': 'Germany'}
    response = make_request('POST', '/products/brands/', token, brand_data)
    brand_id = response.json()['id'] if response and response.status_code == 201 else None
    
    if not category_id or not brand_id:
        print(f"{RED}✗ Impossible de créer les dépendances{RESET}")
        return
    
    # Test: Lister les produits
    response = make_request('GET', '/products/')
    print_test("Lister les produits", response and response.status_code == 200, response)
    
    # Test: Créer un produit
    product_data = {
        'name': f'Plaquettes de freins {int(time.time())}',
        'sku': f'BRAKE-{int(time.time())}',
        'description': 'Plaquettes de freins haute performance',
        'category': category_id,
        'brand': brand_id,
        'price': '49.99',
        'cost': '25.00',
        'stock_quantity': 150,
        'is_active': True
    }
    response = make_request('POST', '/products/', token, product_data)
    print_test("Créer un produit (admin)", response and response.status_code == 201, response)
    
    if response and response.status_code == 201:
        product_id = response.json()['id']
        
        # Test: Récupérer un produit (détails complets)
        response = make_request('GET', f'/products/{product_id}/')
        print_test("Récupérer un produit (détails)", response and response.status_code == 200, response)
        
        # Test: Modifier le stock
        stock_data = {'quantity': 200}
        response = make_request('POST', f'/products/{product_id}/update_stock/', token, stock_data)
        print_test("Mettre à jour le stock", response and response.status_code == 200, response)
        
        # Test: Lister les variantes
        response = make_request('GET', f'/products/{product_id}/variants/')
        print_test("Lister les variantes d'un produit", response and response.status_code == 200, response)
        
        # Test: Créer une variante
        variant_data = {
            'name': 'Essieu avant',
            'sku': f'BRAKE-FRONT-{int(time.time())}',
            'attribute_name': 'position',
            'attribute_value': 'avant',
            'stock_quantity': 100
        }
        response = make_request('POST', f'/products/{product_id}/variants/', token, variant_data)
        print_test("Créer une variante (admin)", response and response.status_code == 201, response)
        
        # Test: Lister les images
        response = make_request('GET', f'/products/{product_id}/images/')
        print_test("Lister les images d'un produit", response and response.status_code == 200, response)

def test_filtering(token):
    """Test les filtres et recherches"""
    print_header("TEST: FILTRES ET RECHERCHES")
    
    # Test: Filtrer par catégorie
    response = make_request('GET', '/products/categories/')
    if response and response.status_code == 200 and len(response.json()) > 0:
        category_id = response.json()[0]['id']
        response = make_request('GET', f'/products/?category={category_id}')
        print_test("Filtrer les produits par catégorie", response and response.status_code == 200, response)
    
    # Test: Recherche textuelle
    response = make_request('GET', '/products/?search=moteur')
    print_test("Rechercher des produits par texte", response and response.status_code == 200, response)
    
    # Test: Filtrer les marques par pays
    response = make_request('GET', '/products/brands/?search=France')
    print_test("Chercher les marques par pays", response and response.status_code == 200, response)
    
    # Test: Filtrer par type de carrosserie
    response = make_request('GET', '/products/car-models/?body_type=sedan')
    print_test("Filtrer les modèles par carrosserie", response and response.status_code == 200, response)
    
    # Test: Produits en vedette
    response = make_request('GET', '/products/featured/')
    print_test("Lister les produits en vedette", response and response.status_code == 200, response)

def test_permissions(token):
    """Test les permissions"""
    print_header("TEST: PERMISSIONS")
    
    # Test: Créer une catégorie sans token (devrait être refusé)
    category_data = {'name': 'Test', 'description': 'Test'}
    response = make_request('POST', '/products/categories/', None, category_data)
    print_test("Rejeter création catégorie (anon)", response and response.status_code == 403, response)
    
    # Test: Lire les catégories sans token (devrait fonctionner)
    response = make_request('GET', '/products/categories/')
    print_test("Autoriser lecture catégories (anon)", response and response.status_code == 200, response)

def print_summary():
    """Affiche le résumé des tests"""
    print_header("RÉSUMÉ DES TESTS")
    total = tests_total
    passed = tests_passed
    failed = tests_failed
    
    if failed == 0:
        status_color = GREEN
        status_text = "✓ SUCCÈS"
    else:
        status_color = RED
        status_text = "✗ ÉCHEC"
    
    print(f"{status_color}{status_text}{RESET}")
    print(f"\nTotal de tests: {total}")
    print(f"{GREEN}Réussis: {passed}{RESET}")
    print(f"{RED}Échoués: {failed}{RESET}")
    print(f"Taux de réussite: {(passed/total*100):.1f}%\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Fonction principale"""
    print(f"{BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Tests API Produits - auto_api                        ║")
    print(f"║     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{RESET}\n")
    
    # Attendre que le serveur soit prêt
    print(f"{YELLOW}Vérification de la disponibilité du serveur...{RESET}")
    for _ in range(10):
        try:
            response = requests.get(f"{BASE_URL}/../")
            if response.status_code == 200:
                print(f"{GREEN}✓ Serveur disponible{RESET}\n")
                break
        except:
            time.sleep(1)
    else:
        print(f"{RED}✗ Le serveur n'est pas disponible{RESET}")
        return
    
    # Obtenir le token
    token = get_auth_token()
    if not token:
        print(f"{RED}✗ Impossible de continuer sans token{RESET}")
        return
    
    # Exécuter les tests
    test_categories(token)
    test_brands(token)
    test_car_models(token)
    test_products(token)
    test_filtering(token)
    test_permissions(token)
    
    # Afficher le résumé
    print_summary()

if __name__ == '__main__':
    main()
