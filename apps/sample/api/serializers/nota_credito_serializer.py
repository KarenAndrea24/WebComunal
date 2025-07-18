from rest_framework import serializers
from apps.sample.api.serializers.cuota_serializer import CuotaSerializer
from apps.sample.api.serializers.detalle_documento_serializer import DetalleDocumentoSerializer
from apps.sample.models.cuota import Cuota
from apps.sample.models.detalle import DetalleDocumento
from apps.sample.models.documento_base import NotaCredito


class NotaCreditoSerializer(serializers.ModelSerializer):
    DocumentLines = serializers.SerializerMethodField()
    Cuotas = serializers.SerializerMethodField()

    class Meta:
        model = NotaCredito
        fields = [
            'id',
            'codigo_cliente',
            'razon_social',
            'moneda',
            'condicion_pago',
            'cuenta_asociada',
            'referencia',
            'fecha_contabilizacion',
            'fecha_vencimiento',
            'fecha_documento',
            'tipo_documento',
            'serie',
            'correlativo',
            'empleado_ventas',
            'propietario',
            'descuento_global',
            'tipo_operacion',
            'tipo_base_imponible',
            'aplica_detraccion',
            'aplica_auto_detraccion',
            'concepto_detraccion',
            'porcentaje_detraccion',
            'base_imponible',
            'impuesto',
            'total_igv',
            'monto_detraccion',
            'operacion_detraccion',
            'estado_fe',
            'tipo_operacion_fe',
            'motivo_nc',
            'descripcion_motivo',
            'tipo_documento_origen',
            'serie_documento_origen',
            'correlativo_origen',
            'comentarios',
            'DocumentLines',
            'Cuotas',
        ]

    def get_DocumentLines(self, obj):
        detalles = DetalleDocumento.objects.filter(
            content_type__model='notacredito',
            object_id=obj.id
        )
        return DetalleDocumentoSerializer(detalles, many=True).data
    
    def get_Cuotas(self, obj):
        cuotas = Cuota.objects.filter(
            content_type__model='notacredito',
            object_id=obj.id
        )
        return CuotaSerializer(cuotas, many=True).data
         