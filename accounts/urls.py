from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterViewSet, 
    UserViewSet, 
    CustomTokenObtainPairView,
    current_user,
    change_password,
    logout
)

# Créer un router pour les ViewSets
router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'users', UserViewSet, basename='user')

# Les patterns d'URL
urlpatterns = [
    # Routes gérées par les routers
    path('', include(router.urls)),

    # Endpoints JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints pour l'utilisateur actuel (simple APIView avec @api_view)
    path('me/', current_user, name='current-user'),
    path('me/change-password/', change_password, name='change-password'),
    path('me/logout/', logout, name='logout'),
]
