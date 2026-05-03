from django.db import transaction
from django.utils import timezone
from .models import Inventaire, LigneInventaire
from apps.catalogue.models import Produit
from apps.stock.services import StockService
from apps.stock.models import StockEvent

class InventaireService:
 
    @staticmethod
    @transaction.atomic
    def lancer_inventaire(responsable, notes='', entrepot=None):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Lancement inventaire : responsable={responsable}, notes={notes}, entrepot={entrepot}")
        
        from datetime import datetime
        ref = f'INV-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        
        inventaire = Inventaire.objects.create(
            reference=ref,
            responsable=responsable,
            notes=notes,
            entrepot=entrepot,
        )
        
        produits = Produit.objects.filter(actif=True)
        if entrepot:
            produits = produits.filter(entrepot=entrepot)
        logger.info(f"Nombre de produits trouvés : {produits.count()}")
        
        lignes = []
        for produit in produits:
            try:
                if entrepot and hasattr(StockService, 'get_stock_par_entrepot'):
                    stock_theorique = StockService.get_stock_par_entrepot(produit, entrepot)
                else:
                    stock_theorique = StockService.get_stock(produit)
            except Exception as e:
                logger.error(f"Erreur calcul stock produit {produit.id}: {e}")
                stock_theorique = 0
            lignes.append(LigneInventaire(
                inventaire=inventaire,
                produit=produit,
                entrepot=entrepot,
                stock_theorique=stock_theorique,
            ))
        LigneInventaire.objects.bulk_create(lignes)
        logger.info(f"Création terminée, {len(lignes)} lignes ajoutées")
        return inventaire
 
    @staticmethod
    @transaction.atomic
    def saisir_comptage(ligne_id, stock_compte, operateur):
        """Saisit le stock compté pour une ligne d'inventaire."""
        ligne = LigneInventaire.objects.select_for_update().get(id=ligne_id)
        ligne.stock_compte = stock_compte
        ligne.save()
        return ligne

    @staticmethod
    @transaction.atomic
    def valider_inventaire(inventaire_id, responsable):
        """
        Valide l'inventaire et applique les écarts comme événements ES.
        """
        inventaire = Inventaire.objects.get(id=inventaire_id)
        lignes_avec_ecart = inventaire.lignes.exclude(ecart=0).filter(valide=False)
 
        for ligne in lignes_avec_ecart:
            if ligne.ecart > 0:
                event_type = StockEvent.AJUSTEMENT_PLUS
            else:
                event_type = StockEvent.AJUSTEMENT_MOINS
 
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
 
        inventaire.statut = Inventaire.STATUT_VALIDE
        inventaire.date_fin = timezone.now()
        inventaire.save()
        return inventaire