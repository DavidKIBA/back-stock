from django.contrib import admin
from .models import Inventaire, LigneInventaire


class LigneInventaireInline(admin.TabularInline):
    model       = LigneInventaire
    extra       = 0
    readonly_fields = ['stock_theorique', 'ecart']
    fields      = ['produit', 'entrepot', 'stock_theorique',
                   'stock_compte', 'ecart', 'valide', 'notes']


@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'statut', 'responsable', 'date_debut', 'date_fin']
    list_filter   = ['statut']
    search_fields = ['reference']
    readonly_fields = ['date_debut', 'date_fin']
    inlines       = [LigneInventaireInline]