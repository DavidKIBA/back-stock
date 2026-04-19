from django.db import models
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
    @property
    def nb_divergences(self):
        return self.lignes.filter(ecart__ne=0).count()
 
    def __str__(self):
        return f'{self.reference} ({self.get_statut_display()})'

class LigneInventaire(models.Model):
    """
    Une ligne = un produit compté durant l'inventaire.
    Écart = stock compté - stock théorique (calculé via ES).
    """
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE,
                                        related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    stock_theorique = models.IntegerField()  # calculé via Event Sourcing au moment du comptage
    stock_compte = models.IntegerField(null=True, blank=True)  # saisie manuelle
    ecart = models.IntegerField(default=0)  # stock_compte - stock_theorique
    valide = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
 
    def save(self, *args, **kwargs):
        if self.stock_compte is not None:
            self.ecart = self.stock_compte - self.stock_theorique
        super().save(*args, **kwargs)
