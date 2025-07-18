from apps.sample.api.serializers.estado_migracion_serializer import EstadoMigracionSerializer
from apps.sample.models.documento_base import Boleta, Factura, NotaCredito, NotaDebito
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


DOCUMENT_MODELS = {
    'factura': Factura,
    'boleta': Boleta,
    'nota-credito': NotaCredito,
    'nota-debito': NotaDebito,
}

class ActualizarEstadoMigracionGenericoView(APIView):
    def patch(self, request, tipo, pk):
        modelo = DOCUMENT_MODELS.get(tipo.lower())
        if not modelo:
            return Response({"error": f"Tipo de documento '{tipo}' no válido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            documento = modelo.objects.get(pk=pk)
        except modelo.DoesNotExist:
            return Response({"error": f"{tipo.capitalize()} con id {pk} no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EstadoMigracionSerializer(data=request.data)
        if serializer.is_valid():
            documento.estado_migracion = serializer.validated_data['estado_migracion']
            documento.descripcion_migracion = serializer.validated_data.get('descripcion_migracion', '')
            documento.save()
            return Response({"success": f"Estado de migración actualizado para {tipo} #{pk}"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
