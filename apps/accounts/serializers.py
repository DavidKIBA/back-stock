from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ces champs doivent être ajoutés ici
        token['role']      = user.role
        token['full_name'] = user.get_full_name()
        token['email']     = user.email
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name',
                  'email', 'role', 'telephone', 'is_active', 'full_name']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'role', 'telephone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)   # ← hacher le mot de passe
        user.save()
        return user