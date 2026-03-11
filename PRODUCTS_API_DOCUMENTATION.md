# Documentation API Produits

Cette documentation couvre tous les endpoints de gestion des produits, catégories, marques, et modèles de voitures.

## Table des matières

1. [Catégories](#catégories)
2. [Marques](#marques)
3. [Modèles de Voitures](#modèles-de-voitures)
4. [Produits](#produits)
5. [Images de Produits](#images-de-produits)
6. [Variantes de Produits](#variantes-de-produits)

---

## Catégories

Gestion des catégories de pièces détachées.

### Lister les catégories

**Endpoint:** `GET /api/products/categories/`

**Permission:** Public

**Paramètres de query:**
- `search`: Recherche par nom ou description
- `ordering`: Tri (name, -name, created_at, -created_at)
- `page`: Pagination

**Exemple de réponse:**
```json
[
  {
    "id": 1,
    "name": "Moteur",
    "slug": "moteur",
    "image": "https://example.com/categories/moteur.jpg",
    "is_active": true,
    "product_count": 15
  }
]
```

### Récupérer une catégorie

**Endpoint:** `GET /api/products/categories/{id}/`

**Permission:** Public

**Exemple de réponse:**
```json
{
  "id": 1,
  "name": "Moteur",
  "slug": "moteur",
  "description": "Pièces détachées du moteur",
  "image": "https://example.com/categories/moteur.jpg",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Créer une catégorie

**Endpoint:** `POST /api/products/categories/`

**Permission:** Admin uniquement

**Body:**
```json
{
  "name": "Suspension",
  "description": "Pièces de suspension",
  "image": "<file>",
  "is_active": true
}
```

### Modifier une catégorie

**Endpoint:** `PUT /api/products/categories/{id}/`

**Permission:** Admin uniquement

### Supprimer une catégorie

**Endpoint:** `DELETE /api/products/categories/{id}/`

**Permission:** Admin uniquement

### Lister les produits d'une catégorie

**Endpoint:** `GET /api/products/categories/{id}/products/`

**Permission:** Public

---

## Marques

Gestion des marques automobiles.

### Lister les marques

**Endpoint:** `GET /api/products/brands/`

**Permission:** Public

**Paramètres de query:**
- `search`: Recherche par nom ou pays
- `ordering`: Tri

**Exemple de réponse:**
```json
[
  {
    "id": 1,
    "name": "Peugeot",
    "slug": "peugeot",
    "country": "France",
    "logo": "https://example.com/brands/peugeot.png",
    "is_active": true
  }
]
```

### Récupérer une marque

**Endpoint:** `GET /api/products/brands/{id}/`

**Permission:** Public

### Créer une marque

**Endpoint:** `POST /api/products/brands/`

**Permission:** Admin uniquement

**Body:**
```json
{
  "name": "Renault",
  "description": "Marque automobile française",
  "country": "France",
  "website": "https://www.renault.com",
  "logo": "<file>",
  "is_active": true
}
```

### Lister les modèles d'une marque

**Endpoint:** `GET /api/products/brands/{id}/car_models/`

**Permission:** Public

### Lister les produits d'une marque

**Endpoint:** `GET /api/products/brands/{id}/products/`

**Permission:** Public

---

## Modèles de Voitures

Gestion des modèles automobiles et leur compatibilité.

### Lister les modèles de voitures

**Endpoint:** `GET /api/products/car-models/`

**Permission:** Public

**Paramètres de query:**
- `brand`: Filtrer par marque (id)
- `body_type`: Filtrer par type (sedan, coupe, suv, hatchback, station_wagon, van, truck, other)
- `is_active`: true/false/all
- `search`: Recherche
- `ordering`: Tri

**Exemple de réponse:**
```json
[
  {
    "id": 1,
    "brand": 1,
    "brand_name": "Peugeot",
    "name": "308",
    "year_start": 2013,
    "year_end": 2021,
    "body_type": "hatchback"
  }
]
```

### Récupérer un modèle de voiture

**Endpoint:** `GET /api/products/car-models/{id}/`

**Permission:** Public

**Réponse complète avec marque détaillée:**
```json
{
  "id": 1,
  "brand": 1,
  "brand_detail": {
    "id": 1,
    "name": "Peugeot",
    "country": "France",
    "website": "https://www.peugeot.com",
    "is_active": true
  },
  "name": "308",
  "slug": "peugeot-308",
  "year_start": 2013,
  "year_end": 2021,
  "body_type": "hatchback",
  "image": "https://example.com/car_models/peugeot_308.jpg",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Créer un modèle de voiture

**Endpoint:** `POST /api/products/car-models/`

**Permission:** Admin uniquement

**Body:**
```json
{
  "brand": 1,
  "name": "308 T9",
  "year_start": 2021,
  "year_end": null,
  "body_type": "hatchback",
  "image": "<file>",
  "is_active": true
}
```

### Lister les produits compatibles

**Endpoint:** `GET /api/products/car-models/{id}/products/`

**Permission:** Public

---

## Produits

Gestion complète des produits.

### Lister les produits

**Endpoint:** `GET /api/products/`

**Permission:** Public

**Paramètres de query:**
- `category`: Filtrer par catégorie (id)
- `brand`: Filtrer par marque (id)
- `is_active`: true/false/all
- `is_featured`: true/false
- `search`: Recherche par nom, description, sku
- `ordering`: Tri (price, -price, stock_quantity, rating, -created_at)

**Exemple de réponse (liste):**
```json
[
  {
    "id": 1,
    "name": "Plaquettes de freins",
    "slug": "plaquettes-de-freins",
    "sku": "BRAKE-PAD-001",
    "category": 2,
    "category_name": "Freins",
    "brand": 3,
    "brand_name": "Bosch",
    "price": "49.99",
    "stock_quantity": 150,
    "is_in_stock": true,
    "rating": 4.5,
    "is_featured": true,
    "primary_image": {
      "id": 1,
      "image": "https://example.com/products/brake-pad.jpg",
      "alt_text": "Plaquettes de freins Bosch",
      "is_primary": true,
      "display_order": 0
    }
  }
]
```

### Récupérer un produit (détails complets)

**Endpoint:** `GET /api/products/{id}/`

**Permission:** Public

**Réponse complète:**
```json
{
  "id": 1,
  "name": "Plaquettes de freins",
  "slug": "plaquettes-de-freins",
  "description": "Plaquettes de freins haute performance",
  "sku": "BRAKE-PAD-001",
  "category": 2,
  "category_detail": {
    "id": 2,
    "name": "Freins",
    "slug": "freins"
  },
  "brand": 3,
  "brand_detail": {
    "id": 3,
    "name": "Bosch",
    "country": "Germany"
  },
  "compatible_car_models": [
    {
      "id": 1,
      "brand": 1,
      "brand_name": "Peugeot",
      "name": "308",
      "year_start": 2013,
      "year_end": 2021,
      "body_type": "hatchback"
    }
  ],
  "price": "49.99",
  "cost": "25.00",
  "discount_percentage": 49.90,
  "stock_quantity": 150,
  "is_in_stock": true,
  "is_low_stock": false,
  "low_stock_alert": 10,
  "weight": "0.5",
  "dimensions": "10 x 8 x 2",
  "warranty_months": 24,
  "is_active": true,
  "is_featured": true,
  "rating": 4.5,
  "number_of_reviews": 12,
  "images": [
    {
      "id": 1,
      "image": "https://example.com/products/brake-pad.jpg",
      "alt_text": "Plaquettes de freins Bosch",
      "is_primary": true,
      "display_order": 0
    }
  ],
  "variants": [
    {
      "id": 1,
      "name": "Essieu avant",
      "sku": "BRAKE-PAD-001-FRONT",
      "attribute_name": "position",
      "attribute_value": "avant",
      "price_modifier": "0.00",
      "final_price": "49.99",
      "stock_quantity": 100,
      "is_in_stock": true,
      "is_active": true
    }
  ],
  "created_by": 1,
  "created_by_username": "admin",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Créer un produit

**Endpoint:** `POST /api/products/`

**Permission:** Admin uniquement

**Body:**
```json
{
  "name": "Plaquettes de freins",
  "description": "Plaquettes de freins haute performance",
  "sku": "BRAKE-PAD-001",
  "category": 2,
  "brand": 3,
  "compatible_car_models_ids": [1, 2],
  "price": "49.99",
  "cost": "25.00",
  "stock_quantity": 150,
  "low_stock_alert": 10,
  "weight": "0.5",
  "dimensions": "10 x 8 x 2",
  "warranty_months": 24,
  "is_active": true,
  "is_featured": true
}
```

### Modifier un produit

**Endpoint:** `PUT /api/products/{id}/`

**Permission:** Admin uniquement

### Modification partielle

**Endpoint:** `PATCH /api/products/{id}/`

**Permission:** Admin uniquement

**Body (exemple - seulement les champs à modifier):**
```json
{
  "stock_quantity": 120,
  "is_featured": false
}
```

### Supprimer un produit

**Endpoint:** `DELETE /api/products/{id}/`

**Permission:** Admin uniquement

### Produits en vedette

**Endpoint:** `GET /api/products/featured/`

**Permission:** Public

Retourne les produits marqués comme `is_featured = true`

### Produits en rupture imminente

**Endpoint:** `GET /api/products/low_stock/`

**Permission:** Admin uniquement

Retourne les produits avec `stock_quantity <= low_stock_alert`

### Produits rupture de stock

**Endpoint:** `GET /api/products/out_of_stock/`

**Permission:** Admin uniquement

Retourne les produits avec `stock_quantity = 0`

### Mettre à jour le stock

**Endpoint:** `POST /api/products/{id}/update_stock/`

**Permission:** Admin uniquement

**Body:**
```json
{
  "quantity": 200
}
```

**Réponse:**
```json
{
  "id": 1,
  "stock_quantity": 200
}
```

---

## Images de Produits

Gestion des images des produits.

### Lister les images d'un produit

**Endpoint:** `GET /api/products/{id}/images/`

**Permission:** Public

**Réponse:**
```json
[
  {
    "id": 1,
    "image": "https://example.com/products/brake-pad.jpg",
    "alt_text": "Plaquettes de freins Bosch",
    "is_primary": true,
    "display_order": 0
  }
]
```

### Ajouter une image à un produit

**Endpoint:** `POST /api/products/{id}/images/`

**Permission:** Admin uniquement

**Body (multipart/form-data):**
```
image: <file>
alt_text: "Description de l'image"
is_primary: true
display_order: 0
```

### Lister toutes les images

**Endpoint:** `GET /api/products/images/?product_id=1`

**Permission:** Public

### Récupérer une image

**Endpoint:** `GET /api/products/images/{id}/`

**Permission:** Public

### Supprimer une image

**Endpoint:** `DELETE /api/products/images/{id}/`

**Permission:** Admin uniquement

---

## Variantes de Produits

Gestion des variantes (couleur, taille, version, etc.).

### Lister les variantes d'un produit

**Endpoint:** `GET /api/products/{id}/variants/`

**Permission:** Public

**Réponse:**
```json
[
  {
    "id": 1,
    "name": "Essieu avant",
    "sku": "BRAKE-PAD-001-FRONT",
    "attribute_name": "position",
    "attribute_value": "avant",
    "price_modifier": "0.00",
    "final_price": "49.99",
    "stock_quantity": 100,
    "is_in_stock": true,
    "is_active": true
  }
]
```

### Ajouter une variante

**Endpoint:** `POST /api/products/{id}/variants/`

**Permission:** Admin uniquement

**Body:**
```json
{
  "name": "Essieu avant",
  "sku": "BRAKE-PAD-001-FRONT",
  "attribute_name": "position",
  "attribute_value": "avant",
  "price_modifier": "0.00",
  "stock_quantity": 100,
  "is_active": true
}
```

### Types d'attributs disponibles

- `color` - Couleur
- `size` - Taille
- `version` - Version
- `material` - Matière
- `fit` - Ajustement
- `strength` - Puissance
- `other` - Autre

### Lister toutes les variantes

**Endpoint:** `GET /api/products/variants/?product_id=1`

**Permission:** Public

### Récupérer une variante

**Endpoint:** `GET /api/products/variants/{id}/`

**Permission:** Public

### Modifier une variante

**Endpoint:** `PUT /api/products/variants/{id}/`

**Permission:** Admin uniquement

### Supprimer une variante

**Endpoint:** `DELETE /api/products/variants/{id}/`

**Permission:** Admin uniquement

---

## Codes de Statut HTTP

- **200 OK**: Succès
- **201 Created**: Ressource créée
- **204 No Content**: Suppression réussie
- **400 Bad Request**: Données invalides
- **401 Unauthorized**: Authentification requise
- **403 Forbidden**: Permission refusée
- **404 Not Found**: Ressource non trouvée
- **500 Internal Server Error**: Erreur serveur

## Erreurs communes

### Erreur de validation

```json
{
  "field_name": ["Error message"]
}
```

Exemple:
```json
{
  "sku": ["Ce SKU existe déjà."],
  "name": ["Le nom du produit ne peut pas être vide."]
}
```

### Erreur de permission

```json
{
  "detail": "Permission denied"
}
```

### Erreur 404

```json
{
  "detail": "Not found."
}
```

---

## Notes d'implémentation

### Slugs automatiques

Les champs `slug` sont générés automatiquement à partir des champs `name` s'ils ne sont pas fournis.

### Images primaires

Une seule image peut être marquée comme `is_primary` par produit. Marquer une nouvelle image comme primaire désactivera automatiquement la précédente.

### Variantes

Les variantes héritent du produit parent pour les informations de base et permettent des modifications de prix et de stock spécifiques.

### Compatibilité véhicules

Un produit peut être compatible avec plusieurs modèles de voitures via la relation Many-to-Many `compatible_car_models`.

### Indexes de performance

Les modèles incluent des indexes sur:
- SKU (recherche rapide)
- Slug (URLs)
- Category, Brand (filtrage)
- is_active (filtrage des produits actifs)
- Product ID dans les modèles liés

