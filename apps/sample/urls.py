from django.urls import path
from .views import CargaMasivaPreviewView, DocumentoDeleteView, RegistrarDocumentosView, SampleView, boletas_json, documento_detalle, facturas_json, notas_credito_json, notas_debito_json


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


    # urls.py
    path('documentos/<int:pk>/', documento_detalle, name='doc-detalle'),
    # path('documentos/<int:pk>/editar/', DocumentoUpdateView.as_view(), name='doc-editar'),
    # path('documentos/<int:pk>/', DocumentoDeleteView.as_view(), name='doc-borrar'),  # DELETE via AJAX
    path("documentos/<int:pk>/", DocumentoDeleteView.as_view(), name="documento_delete"),

]
