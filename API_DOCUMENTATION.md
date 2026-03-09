# API Documentation - Système d'Authentification Auto API

## Vue d'ensemble
Cette API fournit un système d'authentification complet utilisant Django REST Framework et JWT (JSON Web Tokens) pour la plateforme d'e-commerce de pièces détachées de voitures.

## Endpoints d'Authentification

### 1. Inscription (Register)
**Endpoint:** `POST /api/auth/register/`  
**Description:** Créer un nouvel utilisateur

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "message": "Utilisateur créé avec succès.",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2026-03-08T23:22:00Z"
    }
}
```

**Erreurs possibles:**
- 400: Email existe déjà / Mots de passe ne correspondent pas / Validation échouée

---

### 2. Connexion (Login / Obtenir les tokens JWT)
**Endpoint:** `POST /api/auth/login/`  
**Description:** Obtenir les tokens d'accès et de rafraîchissement

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2026-03-08T23:22:00Z"
    }
}
```

**Erreurs possibles:**
- 401: Identifiants invalides

---

### 3. Rafraîchir le token d'accès
**Endpoint:** `POST /api/auth/token/refresh/`  
**Description:** Obtenir un nouveau token d'accès à partir du refresh token

**Request Body:**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Erreurs possibles:**
- 401: Token invalide ou expiré

---

### 4. Obtenir l'utilisateur actuel
**Endpoint:** `GET /api/auth/users/me/`  
**Description:** Récupérer les informations de l'utilisateur actuellement authentifié

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2026-03-08T23:22:00Z"
}
```

**Erreurs possibles:**
- 401: Token manquant ou invalide

---

### 5. Mettre à jour le profil utilisateur
**Endpoint:** `PUT /api/auth/users/me/`  
**Description:** Mettre à jour les informations du profil utilisateur actuel

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (tous les champs sont optionnels):**
```json
{
    "email": "newemail@example.com",
    "first_name": "Jean",
    "last_name": "Valentin"
}
```

**Response (200 OK):**
```json
{
    "message": "Profil mis à jour avec succès.",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "newemail@example.com",
        "first_name": "Jean",
        "last_name": "Valentin",
        "date_joined": "2026-03-08T23:22:00Z"
    }
}
```

**Erreurs possibles:**
- 400: Email existe déjà
- 401: Token manquant ou invalide

---

### 6. Changer le mot de passe
**Endpoint:** `POST /api/auth/users/me/change-password/`  
**Description:** Changer le mot de passe de l'utilisateur actuel

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "old_password": "AncienMotDePasse123!",
    "new_password": "NouveauMotDePasse456!",
    "new_password2": "NouveauMotDePasse456!"
}
```

**Response (200 OK):**
```json
{
    "message": "Mot de passe changé avec succès."
}
```

**Erreurs possibles:**
- 400: L'ancien mot de passe est incorrect / Les nouveaux mots de passe ne correspondent pas
- 401: Token manquant ou invalide

---

### 7. Déconnexion (Logout)
**Endpoint:** `POST /api/auth/users/me/logout/`  
**Description:** Endpoint de déconnexion (informatif - avec JWT, la déconnexion se fait côté client)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Déconnecté avec succès."
}
```

---

### 8. Lister tous les utilisateurs (Admin)
**Endpoint:** `GET /api/auth/users/`  
**Description:** Lister tous les utilisateurs (accès admin uniquement)

**Headers:**
```
Authorization: Bearer <access_token_admin>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2026-03-08T23:22:00Z"
    },
    ...
]
```

**Erreurs possibles:**
- 403: Accès refusé (non-admin)
- 401: Token manquant ou invalide

---

### 9. Récupérer un utilisateur
**Endpoint:** `GET /api/auth/users/{id}/`  
**Description:** Récupérer les informations d'un utilisateur spécifique

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2026-03-08T23:22:00Z"
}
```

**Erreurs possibles:**
- 404: Utilisateur non trouvé
- 401: Token manquant ou invalide

---

### 10. Mettre à jour un utilisateur
**Endpoint:** `PUT /api/auth/users/{id}/`  
**Description:** Mettre à jour les informations d'un utilisateur

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "first_name": "Jean",
    "last_name": "Valentin"
}
```

**Note:** L'utilisateur ne peut mettre à jour que son propre profil, sauf s'il est admin.

**Erreurs possibles:**
- 403: Accès refusé
- 404: Utilisateur non trouvé
- 401: Token manquant ou invalide

---

### 11. Supprimer un utilisateur
**Endpoint:** `DELETE /api/auth/users/{id}/`  
**Description:** Supprimer un utilisateur

**Headers:**
```
Authorization: Bearer <access_token>
```

**Note:** L'utilisateur ne peut supprimer que son propre compte, sauf s'il est admin.

**Response (204 No Content)**

**Erreurs possibles:**
- 403: Accès refusé
- 404: Utilisateur non trouvé
- 401: Token manquant ou invalide

---

## Configuration JWT

### Tokens
- **Access Token**: Valide 15 minutes
- **Refresh Token**: Valide 1 jour
- **Rotation**: Les refresh tokens sont renouvelés à chaque utilisation

### Headers d'authentification
```
Authorization: Bearer <access_token>
```

### Payload du token d'accès
```json
{
    "token_type": "access",
    "exp": 1234567890,
    "iat": 1234567800,
    "jti": "abcdef123456",
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com"
}
```

---

## Meilleures pratiques d'utilisation

1. **Stockage des tokens**: 
   - Stockez le JWT dans un cookie HTTP-Only ou dans le localStorage du navigateur
   - Ne stockez jamais le token dans le code source

2. **Renouvellement du token**: 
   - Renouveler le token automatiquement avant qu'il n'expire
   - Gérer les erreurs 401 en redirigeant l'utilisateur vers la page de connexion

3. **Sécurité**: 
   - Utilisez toujours HTTPS en production
   - Validez les mots de passe (minimum 8 caractères, mélange de caractères)

4. **Gestion des erreurs**: 
   - Gérez les erreurs 400 (validation) et 401 (authentification)
   - Affichez des messages d'erreur clairs à l'utilisateur

---

## Codes de statut HTTP

- `200 OK`: Requête réussie
- `201 Created`: Ressource créée avec succès
- `204 No Content`: Requête réussie, pas de contenu à retourner
- `400 Bad Request`: Erreur de validation ou de format
- `401 Unauthorized`: Token manquant ou invalide, identifiants incorrects
- `403 Forbidden`: Accès refusé (permissions insuffisantes)
- `404 Not Found`: Ressource non trouvée

---

## Installation et démarrage

```bash
# Installer les dépendances
pip install -r requirements.txt

# Exécuter les migrations
python manage.py migrate

# Créer un super-utilisateur (admin)
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

---

## Exemple de flux d'authentification complet

### 1. Utilisateur s'inscrit
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Utilisateur se connecte
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123!"
  }'
```

### 3. Utilisateur accède à ses informations
```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### 4. Renouveler le token d'accès
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

---

## Architecture et meilleures pratiques

Ce système d'authentification suit les meilleures pratiques de développement:

- **Separation of Concerns**: Utilisation de serializers, viewsets et routers
- **Security**: Validation des mots de passe, gestion des permissions, authentification JWT
- **RESTful**: Endpoints conformes aux principes REST
- **Documentation**: Docstrings et commentaires explicites
- **Scalabilité**: Architecture modulaire et extensible
