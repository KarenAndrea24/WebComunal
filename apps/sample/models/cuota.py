from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


class Cuota(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    documento = GenericForeignKey('content_type', 'object_id')

    fecha = models.DateField()
    porcentaje = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=18, decimal_places=2)

    def clean(self):
        allowed_models = ['factura', 'boleta', 'notacredito', 'notadebito']
        if self.content_type.model not in allowed_models:
            raise ValidationError(f"No se puede asociar Cuota al modelo '{self.content_type.model}'")