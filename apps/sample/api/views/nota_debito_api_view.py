from rest_framework.generics import ListAPIView
from apps.sample.api.serializers.nota_debito_serializer import NotaDebitoSerializer
from apps.sample.models.documento_base import NotaDebito


class NotaDebitoApiView(ListAPIView):
    serializer_class = NotaDebitoSerializer

    def get_queryset(self):
        queryset = NotaDebito.objects.filter(estado_migracion='pendiente')
        id_param = self.request.query_params.get('id')
        if id_param:
            queryset = queryset.filter(id=id_param)
        return queryset
