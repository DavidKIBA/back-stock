from django.shortcuts import render
from accounts.permissions import IsAdmin, IsManagerOrAbove, IsAuthenticated
 
class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
 
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]  # Seul l'admin peut modifier les catégories
        return [IsAuthenticated()]  # Tout le monde peut lire
 
 
class InventaireViewSet(viewsets.ModelViewSet):
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer
 
    def get_permissions(self):
        if self.action in ['create', 'valider']:
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]
