from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Categorie, Produit, Entrepot
from .serializers import CategorieSerializer, ProduitSerializer, EntrepotSerializer
from apps.accounts.permissions import IsAdmin, IsAuthenticated

class CategorieViewSet(viewsets.ModelViewSet):
    queryset         = Categorie.objects.filter(active=True)
    serializer_class = CategorieSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['nom', 'code']
    ordering_fields  = ['ordre', 'nom']
 
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
 
class ProduitViewSet(viewsets.ModelViewSet):
    queryset         = Produit.objects.filter(actif=True).select_related('categorie')
    serializer_class = ProduitSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'emplacement', 'actif']
    search_fields    = ['nom', 'reference', 'description']
    ordering_fields  = ['nom', 'reference', 'prix_unitaire']
 
    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]

class EntrepotViewSet(viewsets.ModelViewSet):
    queryset         = Entrepot.objects.filter(actif=True)
    serializer_class = EntrepotSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['nom', 'code']
    ordering_fields  = ['nom', 'code']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class CategorieViewSet(viewsets.ModelViewSet):
    queryset         = Categorie.objects.filter(active=True)
    serializer_class = CategorieSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['nom', 'code']
    ordering_fields  = ['ordre', 'nom']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class ProduitViewSet(viewsets.ModelViewSet):
    queryset         = Produit.objects.filter(actif=True).select_related('categorie', 'entrepot')
    serializer_class = ProduitSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'entrepot', 'actif']
    search_fields    = ['nom', 'reference', 'description']
    ordering_fields  = ['nom', 'reference', 'prix_unitaire']

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]