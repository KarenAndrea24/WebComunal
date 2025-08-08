from apps.sample.api.serializers.auxiliares import CondicionPagoSerializer, CuentaContableSerializer, EmpleadoSerializer, PropietarioSerializer
from apps.sample.models.maestro import CondicionPago, CuentaContable, Empleado, Propietario
from rest_framework import generics

def build_list_create_view(model, serializer):
    class _View(generics.ListCreateAPIView):
        queryset = model.objects.all().order_by("id")
        serializer_class = serializer
        # permission_classes = [permissions.AllowAny]  # cámbialo según tu necesidad (IsAuthenticated, etc.)
    _View.__name__ = f"{model.__name__}ListCreateAPIView"
    return _View

# List + Create
CondicionPagoAPIView  = build_list_create_view(CondicionPago,  CondicionPagoSerializer)
CuentaContableAPIView = build_list_create_view(CuentaContable, CuentaContableSerializer)
EmpleadoAPIView       = build_list_create_view(Empleado,       EmpleadoSerializer)
PropietarioAPIView    = build_list_create_view(Propietario,    PropietarioSerializer)
