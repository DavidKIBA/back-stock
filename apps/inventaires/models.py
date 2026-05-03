from django.db import models
from datetime import datetime
from django.conf import settings
from apps.catalogue.models import Produit, Categorie, Entrepot
import uuid 
# Create your models here.

class Inventaire(models.Model):
    """
    Une session d'inventaire physique.
    On compte le stock réel et on compare avec le stock théorique (ES).
    """
    STATUT_EN_COURS  = 'EN_COURS'
    STATUT_VALIDE    = 'VALIDE'
    STATUT_ANNULE    = 'ANNULE'
    STATUTS = [
        (STATUT_EN_COURS, 'En cours'),
        (STATUT_VALIDE,   'Validé'),
        (STATUT_ANNULE,   'Annulé'),
    ]
 
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference   = models.CharField(max_length=30, unique=True)  # ex: INV-2026-04
    statut      = models.CharField(max_length=15, choices=STATUTS, default=STATUT_EN_COURS)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes       = models.TextField(blank=True)
    date_debut  = models.DateTimeField(auto_now_add=True)
    date_fin    = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    entrepot    = models.ForeignKey(          # ← champ manquant
                    Entrepot,
                    on_delete=models.SET_NULL,
                    null=True, blank=True,
                    related_name='inventaires'
                  )
    
    def save(self, *args, **kwargs):
        # Générer automatiquement la référence si elle est vide
        if not self.reference:
            self.reference = f'INV-{datetime.now().strftime("%Y%m%d-%H%M%S")}-{str(uuid.uuid4())[:4].upper()}'
            # Exemple : INV-20260503-171507-A3F2
        super().save(*args, **kwargs)

    @property
    def nb_divergences(self):
        return self.lignes.exclude(ecart=0).filter(valide=False).count()
 
    def __str__(self):
        return f'{self.reference} ({self.get_statut_display()})'

class LigneInventaire(models.Model):
    inventaire      = models.ForeignKey(Inventaire, on_delete=models.CASCADE,
                                        related_name='lignes')
    produit         = models.ForeignKey(Produit, on_delete=models.PROTECT)
    entrepot        = models.ForeignKey(Entrepot, on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name='lignes_inventaire')
    stock_theorique = models.IntegerField(default=0)   # ← default=0 obligatoire
    stock_compte    = models.IntegerField(null=True, blank=True)
    ecart           = models.IntegerField(default=0)
    valide          = models.BooleanField(default=False)
    notes           = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Calculer stock_theorique si absent (création depuis l'admin)
        if not self.stock_theorique and self.produit_id:
            try:
                from apps.stock.services import StockService
                if self.entrepot:
                    self.stock_theorique = StockService.get_stock_par_entrepot(
                        self.produit, self.entrepot
                    )
                else:
                    self.stock_theorique = StockService.get_stock(self.produit)
            except Exception:
                self.stock_theorique = 0   # fallback si le service échoue

        # Calculer l'écart seulement si les deux valeurs sont présentes
        if self.stock_compte is not None and self.stock_theorique is not None:
            self.ecart = self.stock_compte - self.stock_theorique

        super().save(*args, **kwargs)