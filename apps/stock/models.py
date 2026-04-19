from django.db import models
from django.conf import settings
from apps.catalogue.models import Produit, Categorie, Entrepot
import uuid
# Create your models here.

class StockEvent(models.Model):
 
    # ─── Types d'événements ───────────────────────────────
    ENTREE_FOURNISSEUR = 'ENTREE_FOURNISSEUR'   # Livraison fournisseur
    SORTIE_UTILISATION = 'SORTIE_UTILISATION'   # Utilisation / consommation
    SORTIE_VENTE       = 'SORTIE_VENTE'         # Vente directe
    RETOUR_FOURNISSEUR = 'RETOUR_FOURNISSEUR'   # Retour marchandise
    RETOUR_CLIENT      = 'RETOUR_CLIENT'        # Retour d'un client
    TRANSFERT_ENTREE   = 'TRANSFERT_ENTREE'     # Transfert entrant
    TRANSFERT_SORTIE   = 'TRANSFERT_SORTIE'     # Transfert sortant
    AJUSTEMENT_PLUS    = 'AJUSTEMENT_PLUS'      # Correction inventaire +
    AJUSTEMENT_MOINS   = 'AJUSTEMENT_MOINS'     # Correction inventaire -
    INITIALISATION     = 'INITIALISATION'       # Stock de départ
 
    EVENT_TYPES = [
        (ENTREE_FOURNISSEUR, '📦 Entrée Fournisseur'),
        (SORTIE_UTILISATION, '🔧 Sortie Utilisation'),
        (SORTIE_VENTE,       '💰 Sortie Vente'),
        (RETOUR_FOURNISSEUR, '↩️  Retour Fournisseur'),
        (RETOUR_CLIENT,      '↩️  Retour Client'),
        (TRANSFERT_ENTREE,   '➡️  Transfert Entrée'),
        (TRANSFERT_SORTIE,   '⬅️  Transfert Sortie'),
        (AJUSTEMENT_PLUS,    '📋 Ajustement +'),
        (AJUSTEMENT_MOINS,   '📋 Ajustement -'),
        (INITIALISATION,     '🚀 Initialisation'),
    ]

    # ─── Champs ───────────────────────────────────────────
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT,
                                     related_name='events')
    event_type = models.CharField(max_length=25, choices=EVENT_TYPES)
    quantite = models.IntegerField()           # + entrée / - sortie
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    numero_bon = models.CharField(max_length=50, blank=True)  # ex: PO-2024
    fournisseur = models.CharField(max_length=100, blank=True) # ex: Fournisseur X
    entrepot_source = models.ForeignKey(Entrepot, on_delete=models.SET_NULL,
                                          null=True, related_name='events_sortie')
    entrepot_destination = models.ForeignKey(Entrepot, on_delete=models.SET_NULL,
                                          null=True, related_name='events_entree')
    motif = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    operateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, related_name='events_stock')
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()
 
    class Meta:
        ordering = ['-created_at']
        unique_together = ['produit', 'version']
        verbose_name = 'Événement de stock'
    def __str__(self):
        return f'[{self.event_type}] {self.produit.reference} {self.quantite:+d}'

     
    @property
    def valeur(self):
        """Valeur financière de l'événement"""
        prix = self.prix_unitaire or self.produit.prix_unitaire
        return abs(self.quantite) * prix



class StockSnapshot(models.Model):
    """
    Photo du stock à un instant T pour éviter de rejouer
    TOUS les événements à chaque lecture.
    CASCADE : si le produit ou l'entrepôt est supprimé,
    le snapshot n'a plus de sens → supprimé automatiquement.
    """
    produit          = models.ForeignKey(
                         Produit,
                         on_delete=models.CASCADE,
                         related_name='snapshots'
                       )
    entrepot         = models.ForeignKey(
                         Entrepot,
                         on_delete=models.CASCADE,
                         null=True, blank=True,
                         related_name='snapshots'
                       )
    quantite         = models.IntegerField()
    derniere_version = models.PositiveIntegerField()
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['produit', 'entrepot']

    def __str__(self):
        return f'Snapshot {self.produit.reference} : {self.quantite} (v{self.derniere_version})'