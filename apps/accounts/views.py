from django.shortcuts import render
from apps.accounts.permissions import IsAdmin, IsManagerOrAbove, IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, CreateUserSerializer
from .permissions import IsAdmin, IsAuthenticated
from apps.catalogue.models import Categorie
from apps.catalogue.serializers import CategorieSerializer
from apps.inventaires.models import Inventaire
from apps.inventaires.serializers import InventaireSerializer

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
 
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]  # Seul l'admin peut modifier les catégories
        return [IsAuthenticated()]  # Tout le monde peut lire
 
 
class InventaireViewSet(viewsets.ModelViewSet):
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer
 
    def get_permissions(self):
        if self.action in ['create', 'valider']:
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]

class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all().order_by('username')
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['username', 'first_name', 'last_name', 'email']
    ordering_fields  = ['username', 'role']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer   # serializer avec mot de passe
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdmin()]
        return [IsAuthenticated()]