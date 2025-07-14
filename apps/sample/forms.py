# ---------- 2.1  Formulario de cabecera (ejemplo con Factura) ----------
from django import forms
from django.forms import BaseInlineFormSet
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from apps.sample.models.detalle import DetalleDocumento
from apps.sample.models.documento_base import Factura


class FacturaForm(forms.ModelForm):
    class Meta:
        model  = Factura
        # Muestra sólo los campos que vas a editar/visualizar
        exclude = ("serie_documento","estado_fe")           # ejemplo
        widgets = {
            # date-pickers / selects bonitos
            # "fecha_contabilizacion": forms.DateInput(attrs={"type": "date"}),
            # "fecha_vencimiento"   : forms.DateInput(attrs={"type": "date"}),
            # "fecha_documento"     : forms.DateInput(attrs={"type": "date"}),
            "fecha_contabilizacion": forms.DateInput(attrs={"type": "date", "class": "form-control form-control-plaintext", "readonly": True}),
            "fecha_vencimiento"   : forms.DateInput(attrs={"type": "date", "class": "form-control form-control-plaintext", "readonly": True}),
            "fecha_documento"     : forms.DateInput(attrs={"type": "date", "class": "form-control form-control-plaintext", "readonly": True}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({
                "class": "form-control form-control-plaintext mb-1",
                "readonly": True,
                "disabled": True,       # evita tab-focus
            })


# ---------- 2.2  Formset de detalles ----------
class DetalleDocumentoForm(forms.ModelForm):
    class Meta:
        model   = DetalleDocumento
        exclude = ("content_type", "object_id", "documento")

DetalleDocumentoFormSet = generic_inlineformset_factory(
    DetalleDocumento,
    form         = DetalleDocumentoForm,
    extra        = 1, 
    can_delete=True
)