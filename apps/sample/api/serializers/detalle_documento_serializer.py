from apps.sample.models.detalle import DetalleDocumento
from rest_framework import serializers


class DetalleDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleDocumento
        fields = [
            'id',
            'numero_linea',
            'codigo_articulo',
            'descripcion',
            'cantidad',
            'moneda',
            'articulo_unidad',
            'precio_unidad',
            'descuento',
            'total_moneda_extranjera',
            'impuesto',
            'tipo_afectacion_igv',
            'cuenta_mayor',
            'cc1_general',
            'cc2_unidades_negocio',
            'cc3_local',
            'grupo_detraccion',
            'solo_impuesto'
        ]
