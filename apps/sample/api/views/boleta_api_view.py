from apps.sample.api.serializers.boleta_serializer import BoletaSerializer
from rest_framework.generics import ListAPIView
from apps.sample.models.documento_base import Boleta


class BoletaApiView(ListAPIView):
    serializer_class = BoletaSerializer

    def get_queryset(self):
        queryset = Boleta.objects.filter(estado_migracion='pendiente')
        id_param = self.request.query_params.get('id')
        if id_param:
            queryset = queryset.filter(id=id_param)
        return queryset
