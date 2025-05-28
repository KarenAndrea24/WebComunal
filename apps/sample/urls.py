from django.urls import path
from .views import SampleView


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
    )
]
