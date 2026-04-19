# apps/rapports/services.py
from django.db import models as djm
from apps.stock.models import StockEvent
from apps.catalogue.models import Categorie, Produit, Entrepot
from apps.stock.services import StockService


class RapportService:

    @staticmethod
    def rapport_mouvements(date_debut, date_fin,
                           categorie_id=None, entrepot_id=None):
        """Rapport des mouvements filtrés par période, catégorie, entrepôt."""
        qs = StockEvent.objects.filter(
            created_at__date__gte=date_debut,
            created_at__date__lte=date_fin,
        ).select_related(
            'produit', 'produit__categorie',
            'entrepot_source', 'entrepot_destination', 'operateur'
        )

        if categorie_id:
            qs = qs.filter(produit__categorie__id=categorie_id)

        if entrepot_id:
            from django.db.models import Q
            qs = qs.filter(
                Q(entrepot_source__id=entrepot_id) |
                Q(entrepot_destination__id=entrepot_id)
            )

        return {
            'periode':       {'debut': str(date_debut), 'fin': str(date_fin)},
            'total_entrees': qs.filter(quantite__gt=0).aggregate(
                              total=djm.Sum('quantite'))['total'] or 0,
            'total_sorties': abs(qs.filter(quantite__lt=0).aggregate(
                              total=djm.Sum('quantite'))['total'] or 0),
            'mouvements': list(qs.values(
                'created_at', 'produit__nom', 'produit__reference',
                'produit__categorie__nom', 'event_type', 'quantite',
                'entrepot_source__nom', 'entrepot_destination__nom',
                'numero_bon', 'fournisseur', 'motif'
            ))
        }

    @staticmethod
    def rapport_valorisation():
        """État des stocks valorisés par catégorie et par entrepôt."""
        par_categorie = []
        for cat in Categorie.objects.filter(active=True):
            produits = Produit.objects.filter(categorie=cat, actif=True)
            lignes = []
            for p in produits:
                stock = StockService.get_stock(p)
                valeur = stock * float(p.prix_unitaire)
                detail_entrepots = {
                    e.code: StockService.get_stock_par_entrepot(p, e)
                    for e in Entrepot.objects.filter(actif=True)
                }
                lignes.append({
                    'reference':          p.reference,
                    'nom':                p.nom,
                    'stock':              stock,
                    'stock_par_entrepot': detail_entrepots,
                    'prix_unitaire':      float(p.prix_unitaire),
                    'valeur':             valeur,
                    'en_alerte':          stock <= p.seuil_alerte,
                })
            par_categorie.append({
                'categorie': cat.nom,
                'lignes':    lignes,
                'total':     sum(l['valeur'] for l in lignes)
            })
        return par_categorie