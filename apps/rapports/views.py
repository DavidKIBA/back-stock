from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from .services import RapportService
from apps.accounts.permissions import IsManagerOrAbove, IsAuthenticated


class RapportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        type_rapport = request.query_params.get('type', 'etat_stocks')
        entrepot_id  = request.query_params.get('entrepot')
        categorie_id = request.query_params.get('categorie')

        # Calcul des dates selon la période
        periode = request.query_params.get('periode', 'mensuel')
        aujourd_hui = date.today()
        if periode == 'journalier':
            date_debut = aujourd_hui
        elif periode == 'hebdomadaire':
            date_debut = aujourd_hui - timedelta(days=7)
        elif periode == 'mensuel':
            date_debut = aujourd_hui.replace(day=1)
        elif periode == 'trimestriel':
            date_debut = aujourd_hui - timedelta(days=90)
        elif periode == 'annuel':
            date_debut = aujourd_hui.replace(month=1, day=1)
        else:
            date_debut = request.query_params.get('debut', str(aujourd_hui.replace(day=1)))
        date_fin = request.query_params.get('fin', str(aujourd_hui))

        if type_rapport == 'etat_stocks':
            data = RapportService.etat_des_stocks(entrepot_id, categorie_id)
        elif type_rapport == 'analyse_mouvements':
            data = RapportService.rapport_mouvements(date_debut, date_fin, categorie_id, entrepot_id)
        elif type_rapport == 'performance_inventaire':
            data = RapportService.performance_inventaire(date_debut, date_fin)
        elif type_rapport == 'alertes':
            data = RapportService.alertes_recommandations()
        elif type_rapport == 'rotation_stocks':
            data = RapportService.rotation_stocks(date_debut, date_fin)
        elif type_rapport == 'valorisation_financiere':
            data = RapportService.rapport_valorisation()
        else:
            data = RapportService.etat_des_stocks()

        return Response(data)