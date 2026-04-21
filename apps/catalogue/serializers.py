from rest_framework import serializers
from .models import Entrepot, Categorie, Produit, StockUID
from apps.stock.services import StockService



class EntrepotSerializer(serializers.ModelSerializer):
    nb_produits  = serializers.ReadOnlyField()
    valorisation = serializers.SerializerMethodField()

    class Meta:
        model  = Entrepot
        fields = ['id', 'nom', 'code', 'adresse', 'actif', 'nb_produits', 'valorisation']

    def get_valorisation(self, obj):
        return sum(
            StockService.get_stock_par_entrepot(p, obj) * float(p.prix_unitaire)
            for p in Produit.objects.filter(actif=True)
        )


class CategorieSerializer(serializers.ModelSerializer):
    nb_produits = serializers.ReadOnlyField()

    class Meta:
        model  = Categorie
        fields = ['id', 'nom', 'code', 'couleur', 'icone', 'ordre', 'active', 'nb_produits']


class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    entrepot_nom  = serializers.CharField(source='entrepot.nom',  read_only=True)
    stock         = serializers.SerializerMethodField()
    stock_detail  = serializers.SerializerMethodField()
    en_alerte     = serializers.SerializerMethodField()
    valorisation  = serializers.SerializerMethodField()

    class Meta:
        model  = Produit
        fields = [
            'id', 'reference', 'nom', 'description',
            'categorie', 'categorie_nom',
            'entrepot', 'entrepot_nom',
            'prix_unitaire', 'unite', 'seuil_alerte',
            'stock', 'stock_detail', 'en_alerte', 'valorisation',
            'actif', 'created_at'
        ]

    def get_stock(self, obj):
        return StockService.get_stock(obj)

    def get_stock_detail(self, obj):
        from apps.catalogue.models import Entrepot as E
        return {
            e.code: StockService.get_stock_par_entrepot(obj, e)
            for e in E.objects.filter(actif=True)
        }

    def get_en_alerte(self, obj):
        return StockService.get_stock(obj) <= obj.seuil_alerte

    def get_valorisation(self, obj):
        return StockService.get_stock(obj) * float(obj.prix_unitaire)


class StockUIDSerializer(serializers.ModelSerializer):
    produit_nom  = serializers.CharField(source='produit.nom',   read_only=True)
    entrepot_nom = serializers.CharField(source='entrepot.nom',  read_only=True)
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