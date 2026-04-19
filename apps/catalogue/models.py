from django.db import models
import uuid
# Create your models here.
class Categorie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # ex: MAR, ENT, ACC
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#2E75B6')  # couleur hex UI
    icone = models.CharField(max_length=50, blank=True)  # nom icône React
    ordre = models.PositiveIntegerField(default=0)  # ordre d'affichage
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Catégorie'
 
    def __str__(self):
        return f'[{self.code}] {self.nom}'

    @property
    def nb_produits(self):
        return self.produits.filter(active=True).count()

class Entrepot(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom         = models.CharField(max_length=100)        # ex: INLAND STORAGE
    code        = models.CharField(max_length=20, unique=True)  # ex: ILS-01
    adresse     = models.TextField(blank=True)
    responsable = models.ForeignKey('accounts.User', on_delete=models.SET_NULL,
                                    null=True, related_name='entrepots_geres')
    actif       = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.code}] {self.nom}'
    class Meta:
        ordering = ['nom']
        verbose_name = 'Entrepôt'
    
class Produit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=50, unique=True)  # ex: MAR-001
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT,
                                    related_name='produits')
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unite = models.CharField(max_length=20, default='unité')  # pièce, kg, litre...
    entrepot = models.ForeignKey(Entrepot, on_delete=models.SET_NULL,
                              null=True, related_name='produits')
    seuil_alerte = models.PositiveIntegerField(default=5)  # stock minimum
    image = models.ImageField(upload_to='produits/', null=True, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['categorie', 'nom']
        verbose_name = 'Produit'

    def __str__(self):
        return f'{self.reference} — {self.nom}'