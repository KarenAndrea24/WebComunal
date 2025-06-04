from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


class DetalleDocumento(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    documento = GenericForeignKey('content_type', 'object_id')

    numero_linea = models.IntegerField()
    codigo_articulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=19, decimal_places=6)
    moneda = models.CharField(max_length=10)
    articulo_unidad = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    precio_unidad = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    descuento = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    total_moneda_extranjera = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    impuesto = models.CharField(max_length=10)
    tipo_afectacion_igv = models.CharField(max_length=50)  #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 2 EN LENGHT
    cuenta_mayor = models.CharField(max_length=50, null=True, blank=True)
    cc1_general = models.CharField(max_length=50, null=True, blank=True)
    cc2_unidades_negocio = models.CharField(max_length=50, null=True, blank=True)
    cc3_local = models.CharField(max_length=50, null=True, blank=True)
    grupo_detraccion = models.CharField(max_length=50, null=True, blank=True) #aqui se debe de guardar el id no mas osea 01 o debe de guardarse todo el texto tambien? AQUI ES SOLO 3 EN LENGHT
    solo_impuesto = models.BooleanField(default=False)

    def clean(self):
        allowed_models = ['factura', 'boleta', 'notacredito', 'notadebito']
        if self.content_type.model not in allowed_models:
            raise ValidationError(f"No se puede asociar DetalleDocumento al modelo '{self.content_type.model}'")
