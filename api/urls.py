from rest_framework.routers import DefaultRouter
from django.urls import path, include
from apps.catalogue.views import CategorieViewSet, ProduitViewSet, EntrepotViewSet
from apps.stock.views import StockEventViewSet, DashboardView 
from apps.inventaires.views import InventaireViewSet
from apps.rapports.views import RapportView
from apps.accounts.views import UserViewSet  



 
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'entrepots',    EntrepotViewSet,    basename='entrepot')
router.register(r'categories',   CategorieViewSet,   basename='categorie')
router.register(r'produits',     ProduitViewSet,     basename='produit')
router.register(r'stock/events', StockEventViewSet,  basename='stock-event')
router.register(r'inventaires',  InventaireViewSet,  basename='inventaire')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('rapports/',  RapportView.as_view(),   name='rapport'),
]
 
# ─── Résumé des endpoints générés ───────────────────────
# GET    /api/categories/
# POST   /api/categories/         (Admin seulement)
# GET    /api/produits/
# GET    /api/produits/?categorie=<id>&search=moteur
# GET    /api/stock/events/
# POST   /api/stock/events/entree/
# POST   /api/stock/events/sortie/
# GET    /api/inventaires/
# GET    /api/dashboard/
