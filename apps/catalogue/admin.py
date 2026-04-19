from django.contrib import admin
from .models import Entrepot, Categorie, Produit, StockUID

@admin.register(Entrepot)
class EntrepotAdmin(admin.ModelAdmin):
    list_display  = ['code', 'nom', 'actif', 'created_at']
    search_fields = ['nom', 'code']
    list_filter   = ['actif']


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display  = ['code', 'nom', 'couleur', 'ordre', 'active']
    search_fields = ['nom', 'code']
    list_filter   = ['active']
    ordering      = ['ordre']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'nom', 'categorie', 'entrepot',
                     'prix_unitaire', 'seuil_alerte', 'actif']
    search_fields = ['nom', 'reference']
    list_filter   = ['categorie', 'entrepot', 'actif']
    ordering      = ['categorie', 'nom']


@admin.register(StockUID)
class StockUIDAdmin(admin.ModelAdmin):
    list_display  = ['uid', 'produit', 'entrepot', 'etat',
                     'type_code', 'date_expiration']
    search_fields = ['uid', 'produit__nom', 'produit__reference']
    list_filter   = ['etat', 'type_code', 'entrepot']