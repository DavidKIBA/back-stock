from django.shortcuts import render
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import StockEvent
from .serializers import StockEventSerializer
from .services import StockService
from apps.catalogue.models import Produit
from apps.accounts.permissions import IsAuthenticated
from django.utils import timezone  
from apps.inventaires.models import Inventaire    

class StockEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    En lecture seule : on ne modifie JAMAIS les événements !
    Les créations se font via des actions dédiées.
    """
    queryset         = StockEvent.objects.all().select_related('produit','operateur')
    serializer_class = StockEventSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['produit', 'event_type', 'fournisseur']
    search_fields    = ['numero_bon', 'fournisseur', 'motif']
    ordering_fields  = ['created_at', 'version']

    @action(detail=False, methods=['post'], url_path='entree')
    def entree_fournisseur(self, request):
        """POST /api/stock/events/entree/"""
        produit_id = request.data.get('produit')
        quantite   = int(request.data.get('quantite', 0))
        try:
            produit = Produit.objects.get(id=produit_id)
            event = StockService.entree_fournisseur(
                produit=produit,
                quantite=quantite,
                operateur=request.user,
                numero_bon=request.data.get('numero_bon',''),
                fournisseur=request.data.get('fournisseur',''),
            )
            return Response(StockEventSerializer(event).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
 
    @action(detail=False, methods=['post'], url_path='sortie')
    def sortie(self, request):
        """POST /api/stock/events/sortie/"""
        produit_id = request.data.get('produit')
        quantite   = int(request.data.get('quantite', 0))
        event_type = request.data.get('event_type', StockEvent.SORTIE_UTILISATION)
        try:
            produit = Produit.objects.get(id=produit_id)
            event = StockService.sortie(
                produit=produit, quantite=quantite,
                event_type=event_type, operateur=request.user,
                motif=request.data.get('motif',''),
            )
            return Response(StockEventSerializer(event).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        maintenant = timezone.now()
        debut_mois = maintenant.replace(day=1, hour=0, minute=0, second=0)

        produits_actifs = Produit.objects.filter(actif=True)

        # ─── KPIs ─────────────────────────────────────────
        valorisation = StockService.get_valorisation_totale()

        produits_en_stock = sum(
            1 for p in produits_actifs if StockService.get_stock(p) > 0
        )

        total   = produits_actifs.count()
        alertes = sum(
            1 for p in produits_actifs
            if StockService.get_stock(p) <= p.seuil_alerte
        )

        mouvements_mois = StockEvent.objects.filter(
            created_at__gte=debut_mois
        ).count()

        # ─── Répartition financière ────────────────────────
        repartition = StockService.get_valorisation_par_categorie()

        # ─── Stock par entrepôt ────────────────────────────
        stock_entrepots = StockService.get_stock_par_entrepots()

        # ─── Inventaires ──────────────────────────────────
        inventaires_ouverts = Inventaire.objects.filter(
            statut=Inventaire.STATUT_EN_COURS
        ).count()
        divergences = sum(
            i.nb_divergences
            for i in Inventaire.objects.filter(statut=Inventaire.STATUT_EN_COURS)
        )

        # ─── Mouvements récents ────────────────────────────
        recents = StockEvent.objects.select_related(
            'produit', 'produit__categorie',
            'operateur', 'entrepot_source', 'entrepot_destination'
        ).order_by('-created_at')[:10]

        mouvements = [{
            'id':          str(e.id),
            'produit':     e.produit.nom,
            'reference':   e.numero_bon or f'PO-{e.version:04d}',
            'date':        e.created_at.strftime('%d/%m/%Y'),
            'quantite':    e.quantite,
            'type':        e.event_type,
            'source':      e.entrepot_source.nom if e.entrepot_source else '',
            'destination': e.entrepot_destination.nom if e.entrepot_destination else '',
        } for e in recents]

        return Response({
            'kpis': {
                'valorisation_totale': valorisation,
                'produits_en_stock':   produits_en_stock,
                'references_actives':  f'{total - alertes}/{total}',
                'mouvements_mois':     mouvements_mois,
            },
            'repartition_financiere': repartition,
            'stock_par_entrepots':    stock_entrepots,
            'ecarts_inventaires': {
                'divergences':         divergences,
                'inventaires_ouverts': inventaires_ouverts,
            },
            'mouvements_recents': mouvements,
        })