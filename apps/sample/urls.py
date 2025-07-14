from django.urls import path
from .views import CargaMasivaPreviewView, RegistrarDocumentosView, SampleView, boletas_json, facturas_json, notas_credito_json, notas_debito_json


urlpatterns = [
    path(
        "",
        SampleView.as_view(template_name="index.html"),
        name="index",
    ),
    path(
        "carga-masiva/",
        SampleView.as_view(template_name="carga_masiva.html"),
        name="carga-masiva",
    ),
    path(
        "facturas/",
        SampleView.as_view(template_name="facturas.html"),
        name="facturas",
    ),
    path(
        "boletas/",
        SampleView.as_view(template_name="boletas.html"),
        name="boletas",
    ),
    path(
        "notas-credito/",
        SampleView.as_view(template_name="notas_credito.html"),
        name="notas-credito",
    ),
    path(
        "notas-debito/",
        SampleView.as_view(template_name="notas_debito.html"),
        name="notas-debito",
    ),


    path(
        "carga-masiva/previsualización/",
        CargaMasivaPreviewView.as_view(),
        name="carga-masiva-preview",
    ),
    path(
        "carga-masiva/registrar/",
        RegistrarDocumentosView.as_view(),
        name="carga-masiva-registrar",
    ),

    # Facturas
    path('facturas/data/', facturas_json, name='facturas_json'),

    # Boletas
    path('boletas/data/', boletas_json, name='boletas_json'),

    # Notas de crédito
    path('notas_credito/data/', notas_credito_json, name='notas_credito_json'),

    # Notas de débito
    path('notas_debito/data/', notas_debito_json, name='notas_debito_json'),
]
