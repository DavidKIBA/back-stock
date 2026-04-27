from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Inventaire, LigneInventaire
from .serializers import InventaireSerializer, LigneInventaireSerializer
from .services import InventaireService
from apps.accounts.permissions import IsManagerOrAbove, IsAuthenticated

class InventaireViewSet(viewsets.ModelViewSet):
    queryset         = Inventaire.objects.all().select_related(
                        'responsable', 'entrepot'
                       ).prefetch_related('lignes')
    serializer_class = InventaireSerializer

    def get_permissions(self):
        if self.action in ['create', 'lancer', 'valider']:
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='lancer')
    def lancer(self, request):
        """POST /api/inventaires/lancer/"""
        from apps.catalogue.models import Entrepot
        entrepot_id = request.data.get('entrepot')
        entrepot    = Entrepot.objects.get(id=entrepot_id) if entrepot_id else None

        try:
            inventaire = InventaireService.lancer_inventaire(
                responsable=request.user,
                notes=request.data.get('notes', ''),
                entrepot=entrepot,
            )
            return Response(InventaireSerializer(inventaire).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['patch'], url_path='saisir')
    def saisir(self, request, pk=None):
        """PATCH /api/inventaires/<id>/saisir/"""
        try:
            ligne = LigneInventaire.objects.get(
                id=request.data['ligne_id'],
                inventaire__id=pk
            )
            ligne.stock_compte = int(request.data['stock_compte'])
            ligne.save()   # ← déclenche le calcul d'écart automatiquement
            return Response(LigneInventaireSerializer(ligne).data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'], url_path='valider')
    def valider(self, request, pk=None):
        """POST /api/inventaires/<id>/valider/"""
        try:
            inventaire = InventaireService.valider_inventaire(
                inventaire_id=pk,
                responsable=request.user,
            )
            return Response(InventaireSerializer(inventaire).data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)