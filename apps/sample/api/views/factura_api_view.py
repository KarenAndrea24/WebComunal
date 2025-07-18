from apps.sample.api.serializers.factura_serializer import FacturaSerializer
from rest_framework.generics import ListAPIView
from apps.sample.models.documento_base import Factura


class FacturaApiView(ListAPIView):
    serializer_class = FacturaSerializer

    def get_queryset(self):
        queryset = Factura.objects.filter(estado_migracion='pendiente')
        id_param = self.request.query_params.get('id')
        if id_param:
            queryset = queryset.filter(id=id_param)
        return queryset
