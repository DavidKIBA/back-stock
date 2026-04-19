from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from .services import RapportService
from apps.accounts.permissions import IsManagerOrAbove

class RapportView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        # Paramètres optionnels passés dans l'URL
        # GET /api/rapports/?type=mouvements&debut=2026-01-01&fin=2026-04-30
        # GET /api/rapports/?type=valorisation
        type_rapport = request.query_params.get('type', 'valorisation')
        date_debut   = request.query_params.get('debut', str(date.today().replace(day=1)))
        date_fin     = request.query_params.get('fin',   str(date.today()))
        categorie_id = request.query_params.get('categorie')
        entrepot_id  = request.query_params.get('entrepot')

        if type_rapport == 'mouvements':
            data = RapportService.rapport_mouvements(
                date_debut=date_debut,
                date_fin=date_fin,
                categorie_id=categorie_id,
                entrepot_id=entrepot_id,
            )
        else:
            data = RapportService.rapport_valorisation()

        return Response(data)