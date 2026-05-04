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
        
    @staticmethod
    def etat_des_stocks(entrepot_id=None, categorie_id=None):
        """Rapport principal — ce que montre votre screenshot."""
        from apps.catalogue.models import Produit, Categorie, Entrepot
        from apps.stock.services import StockService

        produits = Produit.objects.filter(actif=True)
        if entrepot_id:
            produits = produits.filter(entrepot__id=entrepot_id)
        if categorie_id:
            produits = produits.filter(categorie__id=categorie_id)

        total_valeur = 0
        total_unites = 0
        produits_data = []

        for p in produits:
            stock = StockService.get_stock(p)
            valeur = stock * float(p.prix_unitaire)
            total_valeur += valeur
            total_unites += stock
            produits_data.append({
                'id': str(p.id),
                'nom': p.nom,
                'reference': p.reference,
                'stock': stock,
                'valeur': valeur,
                'seuil_alerte': p.seuil_alerte,
                'en_alerte': stock <= p.seuil_alerte,
                'categorie': p.categorie.nom,
            })

        # Répartition par catégorie avec pourcentages
        repartition = []
        for cat in Categorie.objects.filter(active=True):
            val_cat = sum(
                d['valeur'] for d in produits_data
                if d['categorie'] == cat.nom
            )
            pct = round((val_cat / total_valeur * 100), 1) if total_valeur > 0 else 0
            repartition.append({
                'categorie': cat.nom,
                'valeur': val_cat,
                'pourcentage': pct,
                'couleur': cat.couleur,
            })

        # Top 5 par valeur
        top5 = sorted(produits_data, key=lambda x: x['valeur'], reverse=True)[:5]

        # Produits en stock faible
        stock_faible = [p for p in produits_data if p['en_alerte'] and p['stock'] > 0]

        return {
            'kpis': {
                'total_produits': len(produits_data),
                'valeur_totale':  total_valeur,
                'total_unites':   total_unites,
                'nb_entrepots':   Entrepot.objects.filter(actif=True).count(),
            },
            'repartition_categorie': sorted(repartition, key=lambda x: x['valeur'], reverse=True),
            'top_5_par_valeur':      top5,
            'produits_stock_faible': stock_faible,
        }

    @staticmethod
    def alertes_recommandations():
        """Produits à réapprovisionner."""
        from apps.catalogue.models import Produit
        from apps.stock.services import StockService

        alertes = []
        for p in Produit.objects.filter(actif=True):
            stock = StockService.get_stock(p)
            if stock <= p.seuil_alerte:
                alertes.append({
                    'reference':  p.reference,
                    'nom':        p.nom,
                    'categorie':  p.categorie.nom,
                    'stock':      stock,
                    'seuil':      p.seuil_alerte,
                    'urgence':    stock == 0,
                    'manquant':   max(0, p.seuil_alerte - stock),
                })
        return sorted(alertes, key=lambda x: x['stock'])

    @staticmethod
    def performance_inventaire(date_debut, date_fin):
        """Taux de divergence des inventaires sur une période."""
        from apps.inventaires.models import Inventaire

        invs = Inventaire.objects.filter(
            date_debut__date__gte=date_debut,
            date_debut__date__lte=date_fin,
            statut='VALIDE'
        )
        total_lignes = sum(
            inv.lignes.count() for inv in invs
        )
        total_ecarts = sum(
            inv.lignes.exclude(ecart=0).count() for inv in invs
        )
        taux = round((total_ecarts / total_lignes * 100), 1) if total_lignes > 0 else 0

        return {
            'nb_inventaires':  invs.count(),
            'total_lignes':    total_lignes,
            'total_ecarts':    total_ecarts,
            'taux_divergence': taux,
        }

    @staticmethod
    def rotation_stocks(date_debut, date_fin):
        """Vitesse de rotation par produit."""
        from apps.catalogue.models import Produit
        from apps.stock.models import StockEvent
        from apps.stock.services import StockService
        import django.db.models as djm

        resultats = []
        for p in Produit.objects.filter(actif=True):
            sorties = StockEvent.objects.filter(
                produit=p,
                quantite__lt=0,
                created_at__date__gte=date_debut,
                created_at__date__lte=date_fin,
            ).aggregate(total=djm.Sum('quantite'))['total'] or 0

            stock_actuel = StockService.get_stock(p)
            rotation = round(abs(sorties) / stock_actuel, 2) if stock_actuel > 0 else 0

            resultats.append({
                'reference':     p.reference,
                'nom':           p.nom,
                'sorties':       abs(sorties),
                'stock_actuel':  stock_actuel,
                'taux_rotation': rotation,
                'dormant':       sorties == 0,
            })
        return sorted(resultats, key=lambda x: x['taux_rotation'], reverse=True)