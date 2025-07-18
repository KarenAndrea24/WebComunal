from django.urls import path
from apps.sample.api.views.boleta_api_view import BoletaApiView
from apps.sample.api.views.estado_migracion_api_view import ActualizarEstadoMigracionGenericoView
from apps.sample.api.views.factura_api_view import FacturaApiView
from apps.sample.api.views.nota_credito_api_view import NotaCreditoApiView
from apps.sample.api.views.nota_debito_api_view import NotaDebitoApiView


urlpatterns = [
    # GET: Listado de documentos
    path('facturas/', FacturaApiView.as_view(), name='lista_facturas'),
    path('boletas/', BoletaApiView.as_view(), name='lista_boletas'),
    path('notas-credito/', NotaCreditoApiView.as_view(), name='lista_notas_credito'),
    path('notas-debito/', NotaDebitoApiView.as_view(), name='lista_notas_debito'),

    # PATCH: Actualización de estado y descripcion de migración
    path('<str:tipo>/<int:pk>/actualizar-migracion/', ActualizarEstadoMigracionGenericoView.as_view()),

]