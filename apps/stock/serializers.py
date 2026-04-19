# apps/stock/serializers.py
from rest_framework import serializers
from .models import StockEvent
from apps.catalogue.models import Produit, StockUID


class StockEventSerializer(serializers.ModelSerializer):
    produit_nom              = serializers.CharField(source='produit.nom',       read_only=True)
    produit_reference        = serializers.CharField(source='produit.reference', read_only=True)
    categorie_nom            = serializers.CharField(source='produit.categorie.nom', read_only=True)
    operateur_nom            = serializers.SerializerMethodField()
    event_type_label         = serializers.CharField(source='get_event_type_display', read_only=True)
    entrepot_source_nom      = serializers.CharField(source='entrepot_source.nom',      read_only=True)
    entrepot_destination_nom = serializers.CharField(source='entrepot_destination.nom', read_only=True)
    valeur                   = serializers.ReadOnlyField()

    class Meta:
        model  = StockEvent
        fields = [
            'id', 'produit', 'produit_nom', 'produit_reference', 'categorie_nom',
            'event_type', 'event_type_label', 'quantite', 'prix_unitaire',
            'entrepot_source', 'entrepot_source_nom',
            'entrepot_destination', 'entrepot_destination_nom',
            'numero_bon', 'fournisseur', 'motif', 'valeur',
            'operateur_nom', 'created_at', 'version'
        ]
        read_only_fields = ['version', 'created_at', 'operateur']

    def get_operateur_nom(self, obj):
        return str(obj.operateur) if obj.operateur else 'Système'


class StockUIDSerializer(serializers.ModelSerializer):
    produit_nom  = serializers.CharField(source='produit.nom',  read_only=True)
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)
    etat_label   = serializers.CharField(source='get_etat_display', read_only=True)

    class Meta:
        model  = StockUID
        fields = [
            'id', 'uid', 'type_code',
            'produit', 'produit_nom',
            'entrepot', 'entrepot_nom',
            'etat', 'etat_label',
            'date_expiration', 'notes',
            'created_at', 'updated_at'
        ]