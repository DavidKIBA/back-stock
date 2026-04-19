from rest_framework import serializers
from .models import Inventaire, LigneInventaire

class LigneInventaireSerializer(serializers.ModelSerializer):
    produit_nom     = serializers.CharField(source='produit.nom', read_only=True)
    entrepot_nom    = serializers.CharField(source='entrepot.nom', read_only=True)

    class Meta:
        model  = LigneInventaire
        fields = [
            'id', 'produit', 'produit_nom',
            'entrepot', 'entrepot_nom',
            'stock_theorique', 'stock_compte',
            'ecart', 'valide', 'notes'
        ]
        read_only_fields = ['stock_theorique', 'ecart']


class InventaireSerializer(serializers.ModelSerializer):
    lignes          = LigneInventaireSerializer(many=True, read_only=True)
    responsable_nom = serializers.CharField(source='responsable.get_full_name',
                                            read_only=True)
    entrepot_nom    = serializers.CharField(source='entrepot.nom', read_only=True)
    nb_divergences  = serializers.ReadOnlyField()

    class Meta:
        model  = Inventaire
        fields = [
            'id', 'reference', 'statut',
            'entrepot', 'entrepot_nom',
            'responsable', 'responsable_nom',
            'nb_divergences', 'notes',
            'date_debut', 'date_fin',
            'lignes'
        ]
        read_only_fields = ['reference', 'date_debut', 'date_fin']