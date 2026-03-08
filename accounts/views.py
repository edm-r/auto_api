from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
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


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs.
    Offre des endpoints pour:
    - GET /api/auth/users/ : Lister tous les utilisateurs (admin)
    - GET /api/auth/users/{id}/ : Récupérer un utilisateur
    - PUT /api/auth/users/{id}/ : Mettre à jour un utilisateur
    - DELETE /api/auth/users/{id}/ : Supprimer un utilisateur
    - GET /api/auth/users/me/ : Obtenir l'utilisateur actuel
    - PUT /api/auth/users/me/update/ : Mettre à jour l'utilisateur actuel
    - POST /api/auth/users/me/change-password/ : Changer le mot de passe
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
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # L'utilisateur ne peut modifier/supprimer que ses propres données
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self):
        """
        Retourner l'objet pour les actions detail.
        Si l'id est 'me', retourner l'utilisateur actuel.
        """
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

    def retrieve(self, request, *args, **kwargs):
        """
        Récupérer un utilisateur. Si l'id est 'me', retourner l'utilisateur actuel.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Mettre à jour un utilisateur.
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
        Supprimer un utilisateur.
        L'utilisateur ne peut supprimer que son propre compte.
        """
        instance = self.get_object()
        if instance.id != request.user.id and not request.user.is_staff:
            return Response(
                {'detail': "Vous n'avez pas le droit de supprimer cet utilisateur."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Endpoint pour obtenir ou mettre à jour l'utilisateur actuel.
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UpdateUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    'message': 'Profil mis à jour avec succès.',
                    'user': UserSerializer(request.user).data
                },
                status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Endpoint pour changer le mot de passe de l'utilisateur actuel.
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Mot de passe changé avec succès.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        Endpoint pour la déconnexion.
        Note: Avec JWT, c'est généralement côté client (supprimer le token).
        Cet endpoint est fourni à titre informatif.
        """
        return Response(
            {'message': 'Déconnecté avec succès.'},
            status=status.HTTP_200_OK
        )

