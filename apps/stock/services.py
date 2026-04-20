from django.db import transaction, models
from django.core.exceptions import ValidationError
from .models import StockEvent
from apps.catalogue.models import Produit, Entrepot

class StockService:
 
    @staticmethod
    def _next_version(produit):
        last = StockEvent.objects.filter(produit=produit).order_by('-version').first()
        return (last.version + 1) if last else 1
 
    @staticmethod
    def _event(produit, event_type, quantite, operateur, **kwargs):
        return StockEvent.objects.create(
            produit=produit, event_type=event_type, quantite=quantite,
            operateur=operateur, version=StockService._next_version(produit),
            **kwargs
        )
 
    @staticmethod
    def get_stock(produit):
        result = StockEvent.objects.filter(produit=produit).aggregate(
            total=models.Sum('quantite'))
        return result['total'] or 0
 
    @staticmethod
    @transaction.atomic
    def entree_fournisseur(produit, quantite, operateur, numero_bon='', fournisseur='', prix=None):
        if quantite <= 0:
            raise ValidationError('Quantité doit être positive')
        return StockService._event(
            produit, StockEvent.ENTREE_FOURNISSEUR, +quantite, operateur,
            numero_bon=numero_bon, fournisseur=fournisseur,
            prix_unitaire=prix or produit.prix_unitaire
        )

    @staticmethod
    @transaction.atomic
    def sortie(produit, quantite, event_type, operateur, motif=''):
        if quantite <= 0:
            raise ValidationError('Quantité doit être positive')
        stock = StockService.get_stock(produit)
        if stock < quantite:
            raise ValidationError(f'Stock insuffisant: {stock} disponible(s)')
        return StockService._event(
            produit, event_type, -quantite, operateur, motif=motif)
 
    @staticmethod
    def get_valorisation_totale():
        """Calcule la valeur totale du stock (pour le KPI dashboard)"""
        from apps.catalogue.models import Produit as P
        total = 0
        for produit in P.objects.filter(actif=True):
            total += StockService.get_stock(produit) * float(produit.prix_unitaire)
        return total

    @staticmethod
    def get_valorisation_par_categorie():
        """Répartition financière par catégorie (graphe dashboard)"""
        from apps.catalogue.models import Categorie, Produit as P
        result = []
        for cat in Categorie.objects.filter(active=True):
            val = 0
            for p in P.objects.filter(categorie=cat, actif=True):
                val += StockService.get_stock(p) * float(p.prix_unitaire)
            result.append({'categorie': cat.nom, 'code': cat.code,
                           'couleur': cat.couleur, 'valeur': val})
        return result

    # stock/services.py

    @staticmethod
    @transaction.atomic
    def transferer(produit, quantite, entrepot_source, entrepot_destination, operateur, motif=''):
        """
        Transfère du stock d'un entrepôt vers un autre.
        Crée DEUX événements : une sortie + une entrée.
        """
        # Vérifier le stock dans l'entrepôt source
        stock_source = StockService.get_stock_par_entrepot(produit, entrepot_source)
        if stock_source < quantite:
            raise ValidationError(
                f'Stock insuffisant dans {entrepot_source.nom} : {stock_source} disponible(s)'
            )

        # Événement 1 : sortie de l'entrepôt source
        StockService._event(
            produit=produit,
            event_type=StockEvent.TRANSFERT_SORTIE,
            quantite=-quantite,
            operateur=operateur,
            entrepot_source=entrepot_source,
            entrepot_destination=entrepot_destination,
            motif=motif,
        )

        # Événement 2 : entrée dans l'entrepôt destination
        StockService._event(
            produit=produit,
            event_type=StockEvent.TRANSFERT_ENTREE,
            quantite=+quantite,
            operateur=operateur,
            entrepot_source=entrepot_source,
            entrepot_destination=entrepot_destination,
            motif=motif,
        )

    @staticmethod
    def get_stock_par_entrepot(produit, entrepot):
        """Stock d'un produit dans un entrepôt précis."""
        result = StockEvent.objects.filter(
            produit=produit,
            entrepot_destination=entrepot   # entrées
        ).aggregate(entrees=models.Sum('quantite'))

        return result['entrees'] or 0
    
    @staticmethod
    def get_stock_par_entrepots():
        """Stock valorisé pour chaque entrepôt — utilisé par le dashboard."""
        from apps.catalogue.models import Entrepot, Produit
        result = []
        for entrepot in Entrepot.objects.filter(actif=True):
            produits = Produit.objects.filter(actif=True)
            nb  = 0
            val = 0
            for p in produits:
                s = StockService.get_stock_par_entrepot(p, entrepot)
                if s > 0:
                    nb  += 1
                    val += s * float(p.prix_unitaire)
            result.append({
                'id':           str(entrepot.id),
                'nom':          entrepot.nom,
                'code':         entrepot.code,
                'nb_produits':  nb,
                'valorisation': val,
            })
        return result