from django.db import models


class DocumentoBase(models.Model):
    # id_externo = models.CharField(max_length=50, unique=True)
    serie_documento = models.IntegerField(null=True, blank=True)
    codigo_cliente = models.CharField(max_length=15)
    razon_social = models.CharField(max_length=100)
    moneda = models.CharField(max_length=10)
    serie = models.CharField(max_length=10)
    condicion_pago = models.IntegerField(null=True, blank=True)
    cuenta_asociada = models.CharField(max_length=15) # ver si todos son numero para colcoarle integer
    referencia = models.CharField(max_length=100, null=True, blank=True)
    fecha_contabilizacion = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_documento = models.DateField()
    tipo_documento = models.CharField(max_length=2)
    correlativo = models.IntegerField(null=True, blank=True)
    empleado_ventas = models.CharField(max_length=100)
    propietario = models.CharField(max_length=100) # SON IDS QUIZAS DEBERIAN DE SER INTEGER NO CHARFIELD
    descuento_global = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_operacion = models.CharField(max_length=50) #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 2 EN LENGHT
    tipo_base_imponible = models.CharField(max_length=50, null=True, blank=True) #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 2 EN LENGHT
    aplica_detraccion = models.CharField(max_length=1, null=True, blank=True)  #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 1 EN LENGHT
    aplica_auto_detraccion = models.CharField(max_length=1, null=True, blank=True)
    concepto_detraccion = models.CharField(max_length=3, null=True, blank=True)
    porcentaje_detraccion = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    base_imponible = models.DecimalField(max_digits=12, decimal_places=2)
    impuesto = models.DecimalField(max_digits=12, decimal_places=2)
    total_igv = models.DecimalField(max_digits=12, decimal_places=2)
    monto_detraccion = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    operacion_detraccion = models.CharField(max_length=50)  #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 2 EN LENGHT
    estado_fe = models.CharField(max_length=2, default='0')
    tipo_operacion_fe = models.CharField(max_length=100)  #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 4 EN LENGHT
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
