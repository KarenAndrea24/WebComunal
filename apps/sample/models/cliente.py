from django.db import models
from apps.sample.models.maestro import CondicionPago, Departamento, Moneda


class TipoPersona(models.Model):
    codigo_tipo_persona = models.CharField(max_length=4, unique=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo_tio_persona} - {self.descripcion}"


class Cliente(models.Model):
    codigo_cliente = models.CharField(max_length=12, unique=True)
    razon_social = models.CharField(max_length=100)
    ruc_dni = models.CharField(max_length=15, unique=True)
    tipo_persona = models.ForeignKey(TipoPersona, on_delete=models.SET_NULL, null=True, blank=True)
    calle_numero = models.CharField(max_length=100, null=True, blank=True)
    distrito = models.CharField(max_length=100, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_contacto = models.CharField(max_length=50)
    apellidos_contacto = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    condicion_pago = models.ForeignKey(CondicionPago, on_delete=models.SET_NULL, null=True, blank=True)
    moneda = models.ForeignKey(Moneda, on_delete=models.SET_NULL, null=True, blank=True)
