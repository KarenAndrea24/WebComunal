from django.db import models


class CondicionPago(models.Model):
    codigo_condicion_pago = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255) 

class TipoDocumento(models.Model):
    codigo_tipo_documento = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)

class Empleado(models.Model):
    codigo_empleado = models.CharField(max_length=20, unique=True)
    dni = models.CharField(max_length=8, unique=True)
    nombres_apellidos = models.CharField(max_length=255)

class Propietario(models.Model):
    codigo_propietario = models.CharField(max_length=20, unique=True)
    dni = models.CharField(max_length=8, unique=True)
    nombres_apellidos = models.CharField(max_length=255)

class CuentaContable(models.Model):
    codigo_cuenta_contable = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255)

# ------------------------------------------------------------------------------

class Departamento(models.Model):
    codigo_departamento = models.CharField(max_length=4, unique=True)
    descripcion = models.CharField(max_length=100)

class Moneda(models.Model):
    codigo_moneda = models.CharField(max_length=15, unique=True)
    descripcion = models.CharField(max_length=50)
    xodigo_sunat = models.CharField(max_length=20, unique=True)

class Series(models.Model):
    codigo_serie = models.IntegerField()
    descripcion = models.CharField(max_length=50)

class TipoOperacion(models.Model):
    codigo_tipo_operacion = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)

class TipoBaseImponible(models.Model):
    codigo_base_imponible = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)

class OperacionDetraccion(models.Model):
    codigo_operacion_detraccion = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)

class TipoOperacionFE(models.Model):
    codigo_tipo_operacion_fe = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)

class Dimension(models.Model):
    codigo_dimension = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255)

class CentrosCosto(models.Model):
    codigo_centro_costo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=255)
    dimension = models.ForeignKey(Dimension, on_delete=models.SET_NULL, null=True)

class GrupoDetraccion(models.Model):
    codigo_grupo_detraccion = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)

class Articulo(models.Model):
    codigo_articulo = models.CharField(max_length=12, unique=True)
    descripcion = models.CharField(max_length=255)

class Impuesto(models.Model):
    codigo_impuesto = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

class TipoAfectacionIGV(models.Model):
    codigo_tipo_afectacion = models.CharField(max_length=2, unique=True)
    descripcion = models.CharField(max_length=50)
