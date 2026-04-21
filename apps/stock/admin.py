from django.contrib import admin
from .models import StockEvent, StockSnapshot

# @admin.register(StockEvent)
# class StockEventAdmin(admin.ModelAdmin):
#     list_display  = ['produit', 'event_type', 'quantite',
#                      'entrepot_source', 'entrepot_destination',
#                      'operateur', 'created_at', 'version']
#     search_fields = ['produit__nom', 'numero_bon', 'fournisseur', 'motif']
#     list_filter   = ['event_type', 'entrepot_source', 'entrepot_destination']
#     ordering      = ['-created_at']
#     readonly_fields = ['id', 'version', 'created_at']

#     # Interdire toute modification — les events sont immuables
#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False


@admin.register(StockEvent)
class StockEventAdmin(admin.ModelAdmin):
     list_display    = ['produit', 'event_type', 'quantite',
                        'entrepot_source', 'entrepot_destination',
                        'operateur', 'created_at', 'version']
     search_fields   = ['produit__nom', 'numero_bon', 'fournisseur', 'motif']
     list_filter     = ['event_type', 'entrepot_source', 'entrepot_destination']
     ordering        = ['-created_at']
     readonly_fields = ['id', 'version', 'created_at', 'produit', 'event_type',
                        'quantite', 'prix_unitaire', 'numero_bon', 'fournisseur',
                        'motif', 'metadata', 'operateur',
                        'entrepot_source', 'entrepot_destination']

     def has_add_permission(self, request):
         return False          # ← impossible de créer depuis l'admin

     def has_change_permission(self, request, obj=None):
         return False          # ← impossible de modifier

     def has_delete_permission(self, request, obj=None):
         return False          # ← impossible de supprimer  

@admin.register(StockSnapshot)
class StockSnapshotAdmin(admin.ModelAdmin):
    list_display  = ['produit', 'entrepot', 'quantite',
                     'derniere_version', 'updated_at']
    search_fields = ['produit__nom']
    list_filter   = ['entrepot']
    readonly_fields = ['updated_at']


