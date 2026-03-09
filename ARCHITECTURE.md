# Architecture du Système d'Authentification

## Vue d'ensemble

Ce système d'authentification suit les meilleures pratiques Django REST Framework et Django en général. Il utilise une architecture modulaire avec séparation des responsabilités.

---

## Structure des fichiers

```
auto_api/
├── accounts/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_admin.py          # Commande pour créer un super-utilisateur
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py                   # Serializers pour validation et transformation
│   ├── urls.py                          # Routes spécifiques à l'app accounts
│   ├── views.py                         # ViewSets pour les opérations CRUD
│   └── tests.py
│
├── auto_api/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                      # Configuration DRF et JWT
│   ├── urls.py                          # URLs principales incluant accounts
│   └── wsgi.py
│
├── manage.py
├── requirements.txt                     # Dépendances du projet
├── API_DOCUMENTATION.md                 # Documentation complète des endpoints
├── TESTING_GUIDE.md                     # Guide pour tester l'API
└── ARCHITECTURE.md                      # Ce fichier
```

---

## Composants clés

### 1. ViewSets (accounts/views.py)

#### RegisterViewSet
- **Responsabilité**: Gérer l'inscription des utilisateurs
- **Endpoints**:
  - `POST /api/auth/register/`: Créer un nouvel utilisateur
- **Permissions**: AllowAny (accessible à tous)
- **Features**:
  - Validation des données
  - Création d'utilisateur
  - Hachage sécurisé du mot de passe

#### CustomTokenObtainPairView
- **Responsabilité**: Obtenir les tokens JWT
- **Endpoints**:
  - `POST /api/auth/login/`: Connexion et obtention des tokens
- **Personnalisation**:
  - Inclusion des données utilisateur dans la réponse
  - Ajout des infos utilisateur au payload JWT

#### UserViewSet
- **Responsabilité**: Gestion complète des utilisateurs
- **Endpoints**:
  - `GET /api/auth/users/`, `POST`, `PUT`, `DELETE`: Opérations CRUD
  - `GET /api/auth/users/me/`: Obtenir l'utilisateur actuel
  - `PUT /api/auth/users/me/`: Mettre à jour le profil
  - `POST /api/auth/users/me/change-password/`: Changer le mot de passe
  - `POST /api/auth/users/me/logout/`: Déconnexion (informatif)
- **Permissions**:
  - Accès authentifié (JWT)
  - Admin required pour lister tous les utilisateurs
  - Restreint à l'utilisateur lui-même pour les actions personnelles

---

### 2. Serializers (accounts/serializers.py)

Les serializers gèrent la validation et la transformation des données JSON en objets Python et vice versa.

#### UserSerializer
- Affiche les informations publiques d'un utilisateur
- Champs: id, username, email, first_name, last_name, date_joined
- Read-only: id, date_joined

#### RegisterSerializer
- Valide les données d'inscription
- Validation custom:
  - Correspondance des mots de passe
  - Email unique
  - Force du mot de passe (via validate_password)
- Crée l'utilisateur en base de données

#### CustomTokenObtainPairSerializer
- Personnalise la réponse du token
- Ajoute les infos utilisateur au payload JWT
- Inclut username et email dans le token

#### ChangePasswordSerializer
- Valide le changement de mot de passe
- Verify l'ancien mot de passe
- Valide la correspondance des nouveaux mots de passe

#### UpdateUserSerializer
- Permet la mise à jour du profil (email, first_name, last_name)
- Validation: Email unique
- Read-only: username (ne peut pas être changé)

---

### 3. Routers et URLs (accounts/urls.py, auto_api/urls.py)

#### DefaultRouter
- Auto-génère les routes standard CRUD
- Crée les listes et les détails automatiquement
- Enregistre les custom actions avec @action décorateur

#### Routes générées
```
/api/auth/register/              - POST: créer utilisateur
/api/auth/users/                 - GET: lister (admin)
/api/auth/users/{id}/            - GET: détail, PUT: update, DELETE: delete
/api/auth/users/me/              - GET: profil actuel
/api/auth/users/me/change-password/ - POST: changer mot de passe
/api/auth/login/                 - POST: obtenir tokens
/api/auth/token/refresh/         - POST: renouveller token
```

---

## Meilleures pratiques implémentées

### 1. Sécurité

- **JWT Authentication**: Authentification sans état (stateless)
- **Token Rotation**: Les refresh tokens sont renouvelés automatiquement
- **Password Validation**: 
  - Utilise Django's `validate_password` avec les validateurs standardisés
  - Vérifie la similarité avec les attributs utilisateur
  - Impose une longueur minimale
  - Vérifie les mots de passe communs
- **HTTPS en Production**: Configuration pour SECURE_SSL_REDIRECT
- **CSRF Protection**: Activée pour les éléments sensibles
- **Permissions granulaires**:
  - AllowAny pour register
  - IsAuthenticated pour les opérations utilisateur
  - IsAdminUser pour lister tous les utilisateurs

### 2. Validation des données

- **Serializer-based Validation**: Toute validation via serializers
- **Custom Validators**: 
  - Vérification de l'unicité de l'email
  - Validation des mots de passe correspondants
- **Exception Handling**: Messages d'erreur clairs pour chaque cas

### 3. Architecture et Design

- **DRY (Don't Repeat Yourself)**: 
  - Utilisation des mixins et des classes de base Django
  - Serializers réutilisables
- **Separation of Concerns**:
  - ViewSets: Logique métier
  - Serializers: Validation et transformation
  - URLs: Routing
- **Extensibilité**:
  - Architecture facile à étendre avec d'autres apps (produits, commandes, etc.)
  - Utilisation des best practices Django: CustomTokenObtainPair pour personnalisation

### 4. Performance

- **Queryset Optimization**: 
  - `get_queryset()` bien défini dans les ViewSets
  - Utilisation d'`only()` et `select_related()` si nécessaire
- **Pagination**: Configuration de la pagination par défaut (10 items par page)
- **Token Caching**: JWT ne nécessite pas de base de données pour la validation

### 5. Documentation et Maintenabilité

- **Docstrings**: Chaque classe et méthode est documentée
- **Commentaires explicatifs**: Code clair et compréhensible
- **Error Messages**: Messages d'erreur en français pour l'utilisateur
- **API Documentation**: Documentation complète des endpoints

---

## Flux d'authentification

```
1. Inscription
   Utilisateur -> POST /register/ -> Validation -> Création DB -> Réponse

2. Connexion
   Utilisateur -> POST /login/ -> Authentification -> Génération JWT -> Réponse

3. Requête authentifiée
   Utilisateur -> GET /me/ + Token -> Validation Token -> Opération -> Réponse

4. Renouvellement du token
   Utilisateur -> POST /token/refresh/ + Refresh -> Validation -> Nouveau Access -> Réponse

5. Déconnexion
   Côté client: Supprimer le token du stockage local
   Côté serveur: Aucune action (JWT stateless)
```

---

## Configuration JWT (settings.py)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),      # Expiration du token d'accès
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),         # Expiration du refresh token
    'ROTATE_REFRESH_TOKENS': True,                       # Renouveler à chaque utilisation
    'BLACKLIST_AFTER_ROTATION': True,                    # Invalider l'ancien token
    'ALGORITHM': 'HS256',                                # Algorithme de signature
    'AUTH_HEADER_TYPES': ('Bearer',),                    # Format: Bearer <token>
}
```

---

## Gestion des erreurs

### Codes de statut HTTP utilisés

- **200 OK**: Succès
- **201 Created**: Ressource créée
- **204 No Content**: Suppression réussie
- **400 Bad Request**: Validation échouée
- **401 Unauthorized**: Non authentifié
- **403 Forbidden**: Non autorisé
- **404 Not Found**: Ressource inexistante

### Exemple de réponse d'erreur

```json
{
    "error_field": ["Message d'erreur descriptif"]
}
```

---

## Points d'extension future

1. **OAuth2 Social Authentication**: 
   - Intégration Google, Facebook, etc.
   - Utiliser `django-allauth`

2. **Two-Factor Authentication (2FA)**:
   - SMS ou Email OTP
   - Authenticator apps

3. **User Profiles**:
   - Modèle UserProfile personnalisé
   - Informations additionnelles (adresse, téléphone)

4. **Role-Based Access Control (RBAC)**:
   - Groupes et permissions granulaires
   - Rôles: customer, seller, admin

5. **API Rate Limiting**:
   - `djangorestframework-ratelimit`
   - Protection contre les abus

6. **Email Verification**:
   - Confirmation d'email avant activation
   - Tokens d'activation

7. **Password Reset**:
   - Tokens de réinitialisation
   - Emails de récupération

---

## Tests

Pour tester l'API, référez-vous à [TESTING_GUIDE.md](TESTING_GUIDE.md)

Recommandations:
- Utilisez Postman ou Insomnia pour les tests manuels
- Implémentez des tests unitaires avec pytest-django
- Utilisez factory_boy pour créer des fixtures de test

---

## Déploiement

### Checklist pour la production

- [ ] Changer SECRET_KEY (dans les variables d'environnement)
- [ ] Mettre DEBUG=False
- [ ] Configurer ALLOWED_HOSTS
- [ ] Utiliser une vraie base de données (PostgreSQL recommandé)
- [ ] Configurer HTTPS et CSRF
- [ ] Installer un serveur WSGI (Gunicorn)
- [ ] Configurer les logs et le monitoring
- [ ] Tester l'authentification en production

---

## Ressources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Security Documentation](https://docs.djangoproject.com/en/5.2/topics/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
