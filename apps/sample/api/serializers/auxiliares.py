from apps.sample.api.serializers.base_auxiliar_serializer import BaseAuxiliarSerializer
from apps.sample.models.maestro import CondicionPago, CuentaContable, Empleado, Propietario


class CondicionPagoSerializer(BaseAuxiliarSerializer):
    class Meta(BaseAuxiliarSerializer.Meta):
        model = CondicionPago

class CuentaContableSerializer(BaseAuxiliarSerializer):
    class Meta(BaseAuxiliarSerializer.Meta):
        model = CuentaContable

class EmpleadoSerializer(BaseAuxiliarSerializer):
    class Meta(BaseAuxiliarSerializer.Meta):
        model = Empleado

class PropietarioSerializer(BaseAuxiliarSerializer):
    class Meta(BaseAuxiliarSerializer.Meta):
        model = Propietario