from django.db import models


class DocumentoBase(models.Model):
    # id_externo = models.CharField(max_length=50, unique=True)
    serie_documento = models.IntegerField()
    codigo_cliente = models.CharField(max_length=15)
    razon_social = models.CharField(max_length=100)
    moneda = models.CharField(max_length=10)
    serie = models.CharField(max_length=10)
    condicion_pago = models.IntegerField()
    cuenta_asociada = models.CharField(max_length=15)
    fecha_contabilizacion = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_documento = models.DateField()
    tipo_documento = models.CharField(max_length=2)
    correlativo = models.IntegerField()
    # empleado_ventas = models.CharField(max_length=100, null=True, blank=True)
    propietario = models.CharField(max_length=100)
    # descuento_global = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_operacion = models.CharField(max_length=2)
    tipo_base_imponible = models.CharField(max_length=2)
    aplica_detraccion = models.BooleanField(default=False)
    aplica_auto_detraccion = models.BooleanField(default=False)
    concepto_detraccion = models.CharField(max_length=3)
    porcentaje_detraccion = models.DecimalField(max_digits=18, decimal_places=2)
    base_imponible = models.DecimalField(max_digits=12, decimal_places=2)
    impuesto = models.DecimalField(max_digits=12, decimal_places=2)
    total_igv = models.DecimalField(max_digits=12, decimal_places=2)
    monto_detraccion = models.DecimalField(max_digits=18, decimal_places=2)
    operacion_detraccion = models.CharField(max_length=2)
    estado_fe = models.CharField(max_length=2, default='0')
    tipo_operacion_fe = models.CharField(max_length=4)
    comentarios = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        abstract = True


class Factura(DocumentoBase):
    pass


class Boleta(DocumentoBase):
    pass


class NotaCredito(DocumentoBase):
    motivo_nc = models.CharField(max_length=100)
    descripcion_motivo = models.TextField(null=True, blank=True)
    tipo_documento_origen = models.CharField(max_length=2)
    serie_documento_origen = models.CharField(max_length=4)
    correlativo_origen = models.CharField(max_length=12)


class NotaDebito(DocumentoBase):
    motivo_nd = models.CharField(max_length=100)
    descripcion_motivo = models.TextField(null=True, blank=True)
    tipo_documento_origen = models.CharField(max_length=2)
    serie_documento_origen = models.CharField(max_length=4)
    correlativo_origen = models.CharField(max_length=12)   
