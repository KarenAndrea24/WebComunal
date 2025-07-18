from rest_framework.generics import ListAPIView
from apps.sample.api.serializers.nota_credito_serializer import NotaCreditoSerializer
from apps.sample.models.documento_base import NotaCredito


class NotaCreditoApiView(ListAPIView):
    serializer_class = NotaCreditoSerializer

    def get_queryset(self):
        queryset = NotaCredito.objects.filter(estado_migracion='pendiente')
        id_param = self.request.query_params.get('id')
        if id_param:
            queryset = queryset.filter(id=id_param)
        return queryset
