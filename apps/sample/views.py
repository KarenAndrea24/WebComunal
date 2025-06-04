
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
import pandas as pd
from apps.sample.models.cuota import Cuota
from apps.sample.models.detalle import DetalleDocumento
from apps.sample.models.documento_base import Boleta, Factura, NotaCredito, NotaDebito
from web_project import TemplateLayout
from django.contrib.contenttypes.models import ContentType
from django.utils.dateparse import parse_date
import logging
logger = logging.getLogger(__name__)

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to sample/urls.py file for more pages.
"""


class SampleView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

def limpiar_columnas(df):
    import unidecode
    df.columns = (
        df.columns.str.strip()
                  .str.upper()
                  .str.replace(" ", "_")
                  .str.replace(".", "", regex=False)
                  .map(lambda x: unidecode.unidecode(x))  # quita tildes
    )

    return df


class CargaMasivaPreviewView(View):
    def post(self, request):
        cabecera_file = request.FILES.get('cabecera')
        detalle_file = request.FILES.get('detalle')

        if not cabecera_file or not detalle_file:
            return JsonResponse({"error": "Archivos incompletos"}, status=400)

        try:
            cabecera_df = pd.read_excel(cabecera_file)
            if cabecera_df.empty:
                return JsonResponse({"error": "No se pudo leer el archivo de cabecera. Verifica que sea un excel válido y tenga datos."}, status=400)
        except Exception:
            logger.exception("Error al leer cabecera")
            return JsonResponse({"error": "Error al leer cabecera"}, status=400)

        try:
            detalle_df = pd.read_excel(detalle_file)
            if detalle_df.empty:
                return JsonResponse({"error": "No se pudo leer el archivo de detalle. Verifica que sea un excel válido y tenga datos."}, status=400)
        except Exception:
            logger.exception("Error al leer detalle")
            return JsonResponse({"error": "Error al leer detalle"}, status=400)

        cabecera_df = limpiar_columnas(cabecera_df)
        detalle_df = limpiar_columnas(detalle_df)
        cuotas_data = []

        for row in cabecera_df.fillna("").to_dict(orient='records'):
            if str(row.get("APLICA_DETRACCION", "")).strip().upper().startswith("Y"):
                monto_detraccion = float(row.get("MONTO_DET", 0))
                porcentaje = float(row.get("PORCENTAJE_DET", 0))
                fecha = row.get("FECHA_VENCIMIENTO")
                cuotas_data.append({
                    "ID_DOCUMENTO": row.get("ID_DOCUMENTO"),
                    "FECHA": fecha,
                    "PORCENTAJE": porcentaje,
                    "TOTAL": monto_detraccion
                })

        return JsonResponse({
            "cabecera": cabecera_df.fillna("").to_dict(orient='records'),
            "detalle": detalle_df.fillna("").to_dict(orient='records'),
            "cuotas": cuotas_data
        })


class RegistrarDocumentosView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            cabeceras = data.get("cabeceras")
            detalles_raw = data.get("detalles")
            cuotas_raw = data.get("cuotas", [])

            if not cabeceras or not detalles_raw:
                return JsonResponse({"message": "No se proporcionaron cabeceras o detalles válidos"}, status=400)

            detalles = defaultdict(list)
            for det in detalles_raw:
                doc_id = str(det.get("ID_DOCUMENTO")).strip()
                detalles[doc_id].append(det)

            cuotas = defaultdict(list)
            for q in cuotas_raw:
                cuotas[str(q.get("ID_DOCUMENTO"))].append(q)

            for cab in cabeceras:
                tipo_doc = str(cab.get("TIPO_DOCUMENTO", "")).zfill(2)
                id_doc = str(cab.get("ID_DOCUMENTO", "")).strip()

                modelo = {
                    "01": Factura,
                    "03": Boleta,
                    "07": NotaCredito,
                    "08": NotaDebito
                }.get(tipo_doc)

                if not modelo:
                    continue

                def parse_str(val):
                    return str(val).strip() if val else ""

                def parse_int(val):
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        return None

                def parse_bool(val):
                    return str(val).strip().upper() == "SI"

                def parse_decimal(val):
                    try:
                        if val in [None, '']:
                            return None
                        return Decimal(str(val).replace(',', '').strip())  # por si viene con coma o espacios
                    except (InvalidOperation, ValueError, TypeError):
                        return None

                # Parse fechas
                def parse_f(date_str):
                    if not date_str:
                        return None
                    if isinstance(date_str, str):
                        try:
                            return datetime.fromisoformat(date_str).date()
                        except ValueError:
                            return parse_date(date_str)
                    return date_str

                # NO DEBE DE TRAER CON SIGNOS DE INTERROGACION CORREGIR
                documento = modelo.objects.create(
                    serie_documento=parse_int(cab.get("SERIE")),
                    codigo_cliente=cab.get("CODIGO_CLIENTE"),
                    razon_social=cab.get("RAZON_SOCIAL"),
                    moneda=cab.get("MONEDA"),
                    serie=cab.get("SERIE"),
                    condicion_pago=cab.get("CONDICION_DE_PAGO"),
                    cuenta_asociada=cab.get("CUENTA_ASOCIADA"),
                    fecha_contabilizacion=parse_f(cab.get("FECHA_CONTABILIZACION")),
                    fecha_vencimiento=parse_f(cab.get("FECHA_VENCIMIENTO")),
                    fecha_documento=parse_f(cab.get("FECHA_DOCUMENTO")),
                    tipo_documento=tipo_doc,
                    correlativo=parse_int(cab.get("CORRELATIVO")),
                    empleado_ventas=cab.get("EMPLEADO_VENTAS"),
                    propietario=cab.get("PROPIETARIO"),
                    descuento_global=cab.get("DESCUENTO_GLOBAL", 0.0),
                    tipo_operacion=cab.get("TIPO_DE_OPERACION"),
                    tipo_base_imponible=cab.get("TIPO_DE_BASE_IMPONIBLE"),
                    aplica_detraccion=str(cab.get("APLICA_DETRACCION", "")).strip().upper() == "SI",
                    aplica_auto_detraccion=str(cab.get("ES_AUTO_DETRACCION?", "")).strip().upper() == "SI",
                    concepto_detraccion=cab.get("CONCEPTO_DE_DETRACCION"),
                    porcentaje_detraccion=cab.get("PORCENTAJE_DET."),
                    base_imponible=cab.get("BASE_IMPONIBLE_SIN_IGV"),
                    impuesto=cab.get("IMPUESTO"),
                    total_igv=cab.get("TOTAL_DOCUMENTO_IGV(CALCULABLE)"),
                    monto_detraccion=cab.get("MONTO_DET."),
                    operacion_detraccion=cab.get("OPERACION_DETRACCION"),
                    estado_fe=cab.get("ESTADO_FE"),
                    tipo_operacion_fe=cab.get("TIPO_DE_OPERACION_FE"),
                    comentarios=cab.get("COMENTARIOS", "")
                )

                # Si es nota de crédito
                if tipo_doc == "07":
                    documento.motivo_nc = cab.get("CODIGO_MOTIVO_NOTA_CRÉDITO")
                    documento.descripcion_motivo = cab.get("MOTIVO_NOTA")
                    documento.tipo_documento_origen = cab.get("TIPO_DOCUMENTO_ORIGEN")
                    documento.serie_documento_origen = cab.get("SERIE_DOCUMENTO")
                    documento.correlativo_origen = cab.get("CORRELATIVO_DOCUMENTO")
                    documento.save()

                # Si es nota de débito
                elif tipo_doc == "08":
                    documento.motivo_nd = cab.get("CODIGO_MOTIVO_NOTA_DEBITO")
                    documento.descripcion_motivo = cab.get("MOTIVO_NOTA")
                    documento.tipo_documento_origen = cab.get("TIPO_DOCUMENTO_ORIGEN")
                    documento.serie_documento_origen = cab.get("SERIE_DOCUMENTO")
                    documento.correlativo_origen = cab.get("CORRELATIVO_DOCUMENTO")
                    documento.save()

                # Guardar detalles relacionados
                # GUARDAR A TODOS SEGUN SEAN BOLLEN, INT O DECIMAL IGUAL EN CABECERA
                ct = ContentType.objects.get_for_model(documento)
                for det in detalles.get(id_doc, []):
                    DetalleDocumento.objects.create(
                        content_type=ct,
                        object_id=documento.id,
                        numero_linea=1,
                        codigo_articulo=det.get("CODIGO_DE_ARTICULO"),
                        descripcion=det.get("DESCRIPCION_DEL_ARTICULO"),
                        cantidad=det.get("CANTIDAD"),
                        moneda=det.get("MONEDA"),
                        articulo_unidad=det.get("ARTICULO_POR_UNIDAD"),
                        precio_unidad=det.get("PRECIO_POR_UNIDAD"),
                        descuento=det.get("%_DSCTO"),
                        impuesto=det.get("IMPUESTOS"),
                        total_moneda_extranjera=parse_decimal(det.get("TOTAL_MONEDA_EXTRANJERA")),
                        tipo_afectacion_igv=det.get("TIPO_DE_AFECTACION_IGV"),
                        cuenta_mayor=det.get("CUENTA_DE_MAYOR"),
                        cc1_general=det.get("CC1_-_GENERAL"),
                        cc2_unidades_negocio=det.get("CC2_-_UNIDADES_DE_NEGOCIO"),
                        cc3_local=det.get("CC3_-_LOCALES"),
                        grupo_detraccion=det.get("GRUPO_DE_DETRACCION"),
                        solo_impuesto=str(det.get("SOLO_IMPUESTO", "")).strip().upper() == "S"
                    )

                # Crear cuota si aplica detracción
                if documento.aplica_detraccion:
                    for cuota_data in cuotas.get(id_doc, []):
                        Cuota.objects.create(
                            content_type=ct,
                            object_id=documento.id,
                            fecha=parse_f(cuota_data.get("FECHA", documento.fecha_contabilizacion)),
                            porcentaje=cuota_data.get("PORCENTAJE", documento.porcentaje_detraccion),
                            total=cuota_data.get("TOTAL", documento.monto_detraccion)
                        )

            return JsonResponse({"message": "Documentos registrados exitosamente"}, status=201)

        except Exception:
            logger.exception("Error al guardar documentos")
            return JsonResponse({"message": "Error al guardar documentos"}, status=400)
