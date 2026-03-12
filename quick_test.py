#!/usr/bin/env python
import requests

try:
    print("Test 1: GET /api/products/categories/")
    r = requests.get('http://localhost:8000/api/products/categories/')
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    
    print("\nTest 2: GET /api/products/brands/")
    r = requests.get('http://localhost:8000/api/products/brands/')
    print(f"  Status: {r.status_code}")
    
    print("\nTest 3: GET /api/products/car-models/")
    r = requests.get('http://localhost:8000/api/products/car-models/')
    print(f"  Status: {r.status_code}")
    
    print("\nTest 4: GET /api/products/")
    r = requests.get('http://localhost:8000/api/products/')
    print(f"  Status: {r.status_code}")
    
    print("\n✓ Tous les endpoints répondent!")
    
except Exception as e:
    print(f"✗ Erreur: {e}")
