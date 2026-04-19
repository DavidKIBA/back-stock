from django.db import transaction
from django.utils import timezone
from .models import Inventaire, LigneInventaire
from apps.catalogue.models import Produit
from apps.stock.services import StockService
from apps.stock.models import StockEvent

class InventaireService:
 
    @staticmethod
    @transaction.atomic
    def lancer_inventaire(responsable, notes=''):
        """
        Démarre une session d'inventaire.
        Prend une photo du stock théorique (via ES) pour chaque produit.
        """
        from datetime import datetime
        ref = f'INV-{datetime.now().strftime("%Y-%m")}'
 
        inventaire = Inventaire.objects.create(
            reference=ref,
            responsable=responsable,
            notes=notes,
        )
 
        # Pour chaque produit actif, créer une ligne avec le stock théorique
        produits = Produit.objects.filter(actif=True)
        lignes = []
        for produit in produits:
            stock_theorique = StockService.get_stock(produit)
            lignes.append(LigneInventaire(
                inventaire=inventaire,
                produit=produit,
                stock_theorique=stock_theorique,
            ))
        LigneInventaire.objects.bulk_create(lignes)
        return inventaire
 
    @staticmethod
    @transaction.atomic
    def saisir_comptage(ligne_id, stock_compte, operateur):
        """Saisit le stock compté pour une ligne d'inventaire."""
        ligne = LigneInventaire.objects.select_for_update().get(id=ligne_id)
        ligne.stock_compte = stock_compte
        ligne.save()  # calcule l'écart automatiquement via save()
        return ligne

    @staticmethod
    @transaction.atomic
    def valider_inventaire(inventaire_id, responsable):
        """
        Valide l'inventaire et applique les écarts comme événements ES.
        Chaque écart devient un AJUSTEMENT_PLUS ou AJUSTEMENT_MOINS.
        """
        inventaire = Inventaire.objects.get(id=inventaire_id)
        lignes_avec_ecart = inventaire.lignes.exclude(ecart=0).filter(valide=False)
 
        for ligne in lignes_avec_ecart:
            if ligne.ecart > 0:
                event_type = StockEvent.AJUSTEMENT_PLUS
            else:
                event_type = StockEvent.AJUSTEMENT_MOINS
 
            # Créer l'événement ES pour corriger le stock
            StockService._event(
                produit=ligne.produit,
                event_type=event_type,
                quantite=ligne.ecart,
                operateur=responsable,
                motif=f'Ajustement inventaire {inventaire.reference}',
                metadata={'inventaire_id': str(inventaire.id)}
            )
            ligne.valide = True
            ligne.save()
 
        inventaire.statut   = Inventaire.STATUT_VALIDE
        inventaire.date_fin = timezone.now()
        inventaire.save()
        return inventaire
