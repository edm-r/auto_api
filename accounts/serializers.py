from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'affichage des informations utilisateur.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription d'un nouvel utilisateur.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        """
        Valider que les deux mots de passe correspondent.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )

        # Vérifier si l'email existe déjà
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError(
                {"email": "Un utilisateur avec cet email existe déjà."}
            )

        return attrs

    def create(self, validated_data):
        """
        Créer un nouvel utilisateur avec les données validées.
        """
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Sérializer personnalisé pour l'obtention des tokens JWT.
    Inclut les informations utilisateur dans la réponse.
    """
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajout des informations utilisateur au payload du token
        token['username'] = user.username
        token['email'] = user.email
        return token

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Ajouter les informations utilisateur à la réponse
        user = User.objects.get(username=attrs['username'])
        data['user'] = UserSerializer(user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer pour le changement de mot de passe.
    """
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Valider que les nouveaux mots de passe correspondent.
        """
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def validate_old_password(self, value):
        """
        Valider que l'ancien mot de passe est correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "L'ancien mot de passe est incorrect."
            )
        return value

    def save(self):
        """
        Sauvegarder le nouveau mot de passe.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des informations utilisateur.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        read_only_fields = ('username',)

    def validate_email(self, value):
        """
        Valider que l'email n'existe pas pour un autre utilisateur.
        """
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "Un utilisateur avec cet email existe déjà."
            )
        return value
