from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
)


class RegisterViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour l'inscription des utilisateurs.
    Offre des endpoints pour:
    - POST /api/auth/register/ : Créer un nouvel utilisateur
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        """Retourner un queryset vide pour les opérations non-list."""
        if self.action == 'list':
            return User.objects.none()
        return super().get_queryset()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Endpoint pour enregistrer un nouvel utilisateur.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'Utilisateur créé avec succès.',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )

    def create(self, request, *args, **kwargs):
        """Override la méthode create pour utiliser register au lieu."""
        return self.register(request)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint personnalisé pour l'obtention des tokens JWT.
    Inclut les informations utilisateur dans la réponse.
    """
    serializer_class = CustomTokenObtainPairSerializer


# ============================================================================
# Endpoints pour l'utilisateur actuel (/me/)
# ============================================================================

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    GET /api/auth/me/ - Obtenir le profil utilisateur actuel
    PUT /api/auth/me/ - Mettre à jour le profil utilisateur actuel
    """
    user = request.user
    
    if request.method == 'GET':
        # Récupérer le profil
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Mettre à jour le profil
        serializer = UpdateUserSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Profil mis à jour avec succès.',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    POST /api/auth/me/change-password/ - Changer le mot de passe
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Mot de passe changé avec succès.'},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """
    POST /api/auth/me/logout/ - Déconnexion
    
    Avec JWT, la déconnexion se fait côté client en supprimant le token.
    Cet endpoint est fourni à titre informatif.
    """
    return Response(
        {'message': 'Déconnecté avec succès.'},
        status=status.HTTP_200_OK
    )



class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs.
    Endpoints:
    - GET /api/auth/users/ : Lister tous les utilisateurs (admin)
    - GET /api/auth/users/{id}/ : Récupérer un utilisateur
    - PUT /api/auth/users/{id}/ : Mettre à jour un utilisateur
    - DELETE /api/auth/users/{id}/ : Supprimer un utilisateur
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        """
        Donner les permissions basées sur l'action.
        """
        if self.action == 'list':
            # Seul l'admin peut lister tous les utilisateurs
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/auth/users/{id}/ - Récupérer un utilisateur spécifique
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        PUT /api/auth/users/{id}/ - Mettre à jour un utilisateur
        L'utilisateur ne peut mettre à jour que ses propres données.
        """
        instance = self.get_object()
        if instance.id != request.user.id and not request.user.is_staff:
            return Response(
                {'detail': "Vous n'avez pas le droit de modifier cet utilisateur."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/auth/users/{id}/ - Supprimer un utilisateur
        L'utilisateur ne peut supprimer que son propre compte.
        """
        instance = self.get_object()
        if instance.id != request.user.id and not request.user.is_staff:
            return Response(
                {'detail': "Vous n'avez pas le droit de supprimer cet utilisateur."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

