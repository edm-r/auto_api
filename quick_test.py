#!/usr/bin/env python
import os
import requests

API_BASE_URL = os.environ.get("API_BASE_URL")
if not API_BASE_URL:
    raise RuntimeError(
        "Missing API_BASE_URL. Example: API_BASE_URL=http://localhost:8000/api"
    )

try:
    print("Test 1: GET /api/products/categories/")
    r = requests.get(f"{API_BASE_URL}/products/categories/")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    
    print("\nTest 2: GET /api/products/brands/")
    r = requests.get(f"{API_BASE_URL}/products/brands/")
    print(f"  Status: {r.status_code}")
    
    print("\nTest 3: GET /api/products/car-models/")
    r = requests.get(f"{API_BASE_URL}/products/car-models/")
    print(f"  Status: {r.status_code}")
    
    print("\nTest 4: GET /api/products/")
    r = requests.get(f"{API_BASE_URL}/products/")
    print(f"  Status: {r.status_code}")
    
    print("\n✓ Tous les endpoints répondent!")
    
except Exception as e:
    print(f"✗ Erreur: {e}")
