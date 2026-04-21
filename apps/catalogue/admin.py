from django.contrib import admin
from .models import Entrepot, Categorie, Produit, StockUID
from apps.stock.services import StockService

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
                     'prix_unitaire', 'stock_actuel','seuil_alerte', 'actif']
    search_fields = ['nom', 'reference']
    list_filter   = ['categorie', 'entrepot', 'actif']
    ordering      = ['categorie', 'nom']

    @admin.display(description='Stock actuel')
    def stock_actuel(self, obj):
        try:
            stock = StockService.get_stock(obj)
            if stock <= obj.seuil_alerte:
                return f'⚠️ {stock} {obj.unite}'
            return f'{stock} {obj.unite}'
        except Exception as e:
            return f'Erreur : {e}'


@admin.register(StockUID)
class StockUIDAdmin(admin.ModelAdmin):
    list_display  = ['uid', 'produit', 'entrepot', 'etat',
                     'type_code', 'date_expiration']
    search_fields = ['uid', 'produit__nom', 'produit__reference']
    list_filter   = ['etat', 'type_code', 'entrepot']