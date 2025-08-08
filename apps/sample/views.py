
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView
import pandas as pd
from apps.sample.forms import DetalleDocumentoFormSet, FacturaForm
from apps.sample.models.cuota import Cuota
from apps.sample.models.detalle import DetalleDocumento
from apps.sample.models.documento_base import Boleta, Factura, NotaCredito, NotaDebito
from apps.sample.models.maestro import CondicionPago, CuentaContable, Empleado, Propietario
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

        mapping = {
            "facturas.html": ("Facturas",  "facturas_json"),
            "boletas.html": ("Boletas",  "boletas_json"),
            "notas_credito.html": ("Notas de crédito", "notas_credito_json"),
            "notas_debito.html": ("Notas de débito",  "notas_debito_json"),
        }
        titulo, url_name = mapping.get(self.template_name, (None, None))
        if titulo and url_name:
            from django.urls import reverse
            context["titulo"] = titulo
            context["url_json"] = reverse(url_name)

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
            if str(row.get("?APLICA_DETRACCION?", "")).strip().upper().startswith("Y"):
                try:
                    id_doc = row.get("ID_DOCUMENTO")
                    fecha = row.get("FECHA_VENCIMIENTO")
                    porcentaje = float(row.get("PORCENTAJE_DET", 0))
                    total_documento = float(row.get("TOTAL_DOCUMENTO_IGV(CALCULABLE)", 0))

                    # Segunda cuota: porcentaje aplicado al total de documento con IGV
                    cuota2_total = round((porcentaje / 100) * total_documento, 2)
                    cuota1_total = round(total_documento - cuota2_total, 2)
                    cuota1_pct = 100 - porcentaje

                    cuotas_data.append({
                        "ID_DOCUMENTO": id_doc,
                        "FECHA": fecha,
                        "PORCENTAJE": cuota1_pct,
                        "TOTAL": cuota1_total
                    })
                    cuotas_data.append({
                        "ID_DOCUMENTO": id_doc,
                        "FECHA": fecha,
                        "PORCENTAJE": porcentaje,
                        "TOTAL": cuota2_total
                    })
                except Exception as e:
                    logger.warning(f"Error calculando cuotas para el documento {row.get('ID_DOCUMENTO')}: {e}")

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

            errores = []

            with transaction.atomic():
                for i, cab in enumerate(cabeceras):
                    tipo_doc = str(cab.get("TIPO_DOCUMENTO", "")).zfill(2)
                    id_doc = str(cab.get("ID_DOCUMENTO", "")).strip()

                    modelo = {
                        "01": Factura,
                        "03": Boleta,
                        "07": NotaCredito,
                        "08": NotaDebito
                    }.get(tipo_doc)

                    if not modelo:
                        errores.append(f"[Fila {i+2}] Tipo documento '{tipo_doc}' inválido")
                        continue

                    fk_error = False

                    # condicion de pago
                    condicion_pago_val = cab.get("CONDICION_DE_PAGO")
                    condicion_pago_obj = None
                    if condicion_pago_val:
                        try:
                            condicion_pago_obj = CondicionPago.objects.get(codigo_condicion_pago=condicion_pago_val)
                        except CondicionPago.DoesNotExist:
                            errores.append(f"[Fila {i+2}] condición de pago '{condicion_pago_val}' no existe")
                            logger.warning(f"[Carga masiva] condición de pago '{condicion_pago_val}' no existe en fila {i+2} del excel")
                            fk_error = True

                    # propietario
                    propietario_val = cab.get("PROPIETARIO")
                    propietario_obj = None
                    if propietario_val:
                        try:
                            propietario_obj = Propietario.objects.get(codigo_propietario=propietario_val)
                        except Propietario.DoesNotExist:
                            errores.append(f"[Fila {i+2}] Propietario '{propietario_val}' no existe")
                            logger.warning(f"[Carga masiva] Propietario '{propietario_val}' no existe en fila {i+2} del excel")
                            fk_error = True

                    # empleado ventas
                    empleado_val = cab.get("EMPLEADO_VENTAS")
                    empleado_obj = None
                    if empleado_val:
                        try:
                            empleado_obj = Empleado.objects.get(codigo_empleado=empleado_val)
                        except Empleado.DoesNotExist:
                            errores.append(f"[Fila {i+2}] Empleado ventas '{empleado_val}' no existe")
                            logger.warning(f"[Carga masiva] Empleado ventas '{empleado_val}' no existe en fila {i+2} del excel")
                            fk_error = True
                    
                    # cuenta contable
                    cuenta_val = cab.get("CUENTA_ASOCIADA")
                    cuenta_obj = None
                    if cuenta_val:
                        try:
                            cuenta_obj = CuentaContable.objects.get(codigo_cuenta_contable=cuenta_val)
                        except CuentaContable.DoesNotExist:
                            errores.append(f"[Fila {i+2}] Cuenta contable '{cuenta_val}' no existe.")
                            logger.warning(f"[Carga masiva] Cuenta contable '{cuenta_val}' no existe en fila {i+2} del Excel.")
                            fk_error = True

                    if fk_error:
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
                        # condicion_pago=parse_int(cab.get("CONDICION_DE_PAGO")),
                        condicion_pago=condicion_pago_obj,
                        # cuenta_asociada=cab.get("CUENTA_ASOCIADA"),
                        cuenta_asociada=cuenta_obj,
                        referencia=cab.get("REFERENCIA"),
                        fecha_contabilizacion=parse_f(cab.get("FECHA_CONTABILIZACION")),
                        fecha_vencimiento=parse_f(cab.get("FECHA_VENCIMIENTO")),
                        fecha_documento=parse_f(cab.get("FECHA_DOCUMENTO")),
                        tipo_documento=tipo_doc,
                        correlativo=parse_int(cab.get("CORRELATIVO")),
                        # empleado_ventas=cab.get("EMPLEADO_VENTAS"),
                        empleado_ventas=empleado_obj,
                        # propietario=cab.get("PROPIETARIO"),
                        propietario=propietario_obj,
                        descuento_global=parse_decimal(cab.get("DESCUENTO_GLOBAL", 0.00)),
                        tipo_operacion=cab.get("TIPO_DE_OPERACION"),
                        tipo_base_imponible=cab.get("TIPO_DE_BASE_IMPONIBLE"),
                        # aplica_detraccion=str(cab.get("?APLICA_DETRACCION?", "")).strip().upper() == "Y",
                        # aplica_auto_detraccion=str(cab.get("ES_AUTO_DETRACCION?", "")).strip().upper() == "Y",
                        aplica_detraccion=str(cab.get("?APLICA_DETRACCION?", "")),
                        # valor = parse_str(cab.get("APLICA_DETRACCION"))
                        # aplica_detraccion = valor if valor in ["Y", "N"] else "N"
                        aplica_auto_detraccion=str(cab.get("ES_AUTO_DETRACCION?", "")),
                        concepto_detraccion=cab.get("CONCEPTO_DE_DETRACCION"),
                        porcentaje_detraccion=parse_decimal(cab.get("PORCENTAJE_DET", 0.00)),
                        base_imponible=parse_decimal(cab.get("BASE_IMPONIBLE_SIN_IGV", 0.00)),
                        impuesto=parse_decimal(cab.get("IMPUESTO", 0.00)),
                        total_igv=parse_decimal(cab.get("TOTAL_DOCUMENTO_IGV(CALCULABLE)", 0.00)),
                        monto_detraccion=parse_decimal(cab.get("MONTO_DET", 0.00)),
                        operacion_detraccion=cab.get("OPERACION_DETRACCION"),
                        estado_fe=cab.get("ESTADO_FE"),
                        tipo_operacion_fe=cab.get("TIPO_DE_OPERACION_FE"),
                        comentarios=cab.get("COMENTARIOS", "")
                    )

                    # Si es nota de crédito
                    if tipo_doc == "07":
                        documento.motivo_nc = cab.get("CODIGO_MOTIVO_NOTA_CREDITO")
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
                            cantidad=parse_decimal(det.get("CANTIDAD", 0.00)),
                            moneda=det.get("MONEDA"),
                            articulo_unidad=parse_decimal(det.get("ARTICULO_POR_UNIDAD", 0.00)),
                            precio_unidad=parse_decimal(det.get("PRECIO_POR_UNIDAD", 0.00)),
                            descuento=parse_decimal(det.get("%_DSCTO", 0.00)),
                            impuesto=det.get("IMPUESTOS"),
                            total_moneda_extranjera=parse_decimal(det.get("TOTAL_MONEDA_EXTRANJERA", 0.00)),
                            tipo_afectacion_igv=det.get("TIPO_DE_AFECTACION_IGV"),
                            cuenta_mayor=det.get("CUENTA_DE_MAYOR"),
                            cc1_general=det.get("CC1_-_GENERAL"),
                            cc2_unidades_negocio=det.get("CC2_-_UNIDADES_DE_NEGOCIO"),
                            cc3_local=det.get("CC3_-_LOCALES"),
                            grupo_detraccion=det.get("GRUPO_DE_DETRACCION"),
                            # solo_impuesto=str(det.get("SOLO_IMPUESTO", "")).strip().upper() == "S"
                            solo_impuesto=str(det.get("SOLO_IMPUESTO", ""))
                        )

                    # Crear cuota si aplica detracción
                    cuotas_para_doc = cuotas.get(id_doc)
                    if cuotas_para_doc:
                        for cuota in cuotas_para_doc:
                            # Aquí si falla, aborta todo
                            Cuota.objects.create(
                                content_type=ct,
                                object_id=documento.id,
                                fecha=parse_f(cuota.get("FECHA")),
                                porcentaje=parse_decimal(cuota.get("PORCENTAJE")),
                                total=parse_decimal(cuota.get("TOTAL"))
                            )

            if errores:
                return JsonResponse({"message": "Errores encontrados en la carga masiva", "errores": errores}, status=400)

            return JsonResponse({"message": "Documentos registrados exitosamente"}, status=201)

        except Exception as e:
            logger.exception("Error al guardar documentos")
            return JsonResponse({"message": f"Error al guardar documentos: {str(e)}"}, status=400)


def facturas_json(request):
    """Devuelve la lista de facturas en formato DataTables‐friendly."""
    facturas = Factura.objects.all().values(
        'id', 'serie_documento', 'codigo_cliente', 'razon_social', 'moneda',
        'serie', 'correlativo', 'condicion_pago', 'cuenta_asociada', 'referencia',
        'fecha_contabilizacion', 'fecha_vencimiento', 'fecha_documento',
        'tipo_documento', 'empleado_ventas', 'propietario',
        'descuento_global', 'tipo_operacion', 'tipo_base_imponible',
        'aplica_detraccion', 'aplica_auto_detraccion',
        'concepto_detraccion', 'porcentaje_detraccion',
        'base_imponible', 'impuesto', 'total_igv',
        'monto_detraccion', 'operacion_detraccion',
        'estado_fe', 'tipo_operacion_fe',
        'comentarios'
    )
    data = list(facturas)
    return JsonResponse({'data': data})


def boletas_json(request):
    """Devuelve la lista de boletas en formato DataTables‐friendly."""
    boletas = Boleta.objects.all().values(
        'id', 'serie_documento', 'codigo_cliente', 'razon_social', 'moneda',
        'serie', 'correlativo', 'condicion_pago', 'cuenta_asociada', 'referencia',
        'fecha_contabilizacion', 'fecha_vencimiento', 'fecha_documento',
        'tipo_documento', 'empleado_ventas', 'propietario',
        'descuento_global', 'tipo_operacion', 'tipo_base_imponible',
        'aplica_detraccion', 'aplica_auto_detraccion',
        'concepto_detraccion', 'porcentaje_detraccion',
        'base_imponible', 'impuesto', 'total_igv',
        'monto_detraccion', 'operacion_detraccion',
        'estado_fe', 'tipo_operacion_fe',
        'comentarios'
    )
    data = list(boletas)
    return JsonResponse({'data': data})


def notas_credito_json(request):
    """Devuelve la lista de notas de credito en formato DataTables‐friendly."""
    notas_credito = NotaCredito.objects.all().values(
        'id', 'serie_documento', 'codigo_cliente', 'razon_social', 'moneda',
        'serie', 'correlativo', 'condicion_pago', 'cuenta_asociada', 'referencia',
        'fecha_contabilizacion', 'fecha_vencimiento', 'fecha_documento',
        'tipo_documento', 'empleado_ventas', 'propietario',
        'descuento_global', 'tipo_operacion', 'tipo_base_imponible',
        'aplica_detraccion', 'aplica_auto_detraccion',
        'concepto_detraccion', 'porcentaje_detraccion',
        'base_imponible', 'impuesto', 'total_igv',
        'monto_detraccion', 'operacion_detraccion',
        'estado_fe', 'tipo_operacion_fe',
        'comentarios'
    )
    data = list(notas_credito)
    return JsonResponse({'data': data})


def notas_debito_json(request):
    """Devuelve la lista de notas de débito en formato DataTables‐friendly."""
    notas_debito = NotaDebito.objects.all().values(
        'id', 'serie_documento', 'codigo_cliente', 'razon_social', 'moneda',
        'serie', 'correlativo', 'condicion_pago', 'cuenta_asociada', 'referencia',
        'fecha_contabilizacion', 'fecha_vencimiento', 'fecha_documento',
        'tipo_documento', 'empleado_ventas', 'propietario',
        'descuento_global', 'tipo_operacion', 'tipo_base_imponible',
        'aplica_detraccion', 'aplica_auto_detraccion',
        'concepto_detraccion', 'porcentaje_detraccion',
        'base_imponible', 'impuesto', 'total_igv',
        'monto_detraccion', 'operacion_detraccion',
        'estado_fe', 'tipo_operacion_fe',
        'comentarios'
    )
    data = list(notas_debito)
    return JsonResponse({'data': data})


def documento_detalle(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    form      = FacturaForm(instance=factura)

    content_type = ContentType.objects.get_for_model(Factura)
    detalles = DetalleDocumento.objects.filter(
        content_type=content_type,
        object_id=factura.id
    )

    return render(request, 'documentos/modals/modal_visualizacion_documento.html', {
        'form': form,
        'detalles': detalles
    })

# def documento_editar(request, pk):
#     factura = get_object_or_404(Factura, pk=pk)

#     if request.method == "POST":
#         form      = FacturaForm(request.POST, instance=factura)
#         formset   = DetalleDocumentoFormSet(
#             request.POST,
#             instance=factura,
#             queryset=factura.detalledocumento_set.all()
#         )
#         if form.is_valid() and formset.is_valid():
#             form.save()
#             # formset.save() rellenará automáticamente content_type y object_id
#             formset.save()
#             ...
#     else:
#         form    = FacturaForm(instance=factura)
#         formset = DetalleDocumentoFormSet(instance=factura)

#     return render(request, "documentos/editar.html",
#                   {"form": form, "formset": formset})


class DocumentoDeleteView(View):
    """
    Borra un documento por ID y su tipo (01 factura, 03 boleta, 07 NC, 08 ND).
    También elimina DetalleDocumento y Cuota vinculados por content_type/object_id.
    Soporta:
      - DELETE /documentos/<id>/?tipo=01
    Si no se envía 'tipo', intenta localizar de forma única entre los 4 modelos.
    """

    MODEL_MAP = {
        "01": Factura,
        "03": Boleta,
        "07": NotaCredito,
        "08": NotaDebito,
    }

    def delete(self, request, pk):
        tipo = (request.GET.get("tipo") or "").strip()

        try:
            with transaction.atomic():
                if tipo:
                    model = self.MODEL_MAP.get(tipo)
                    if not model:
                        return JsonResponse({"message": "Tipo de documento inválido."}, status=400)

                    obj = get_object_or_404(model, pk=pk)
                    ct = ContentType.objects.get_for_model(model)

                    DetalleDocumento.objects.filter(content_type=ct, object_id=obj.id).delete()
                    Cuota.objects.filter(content_type=ct, object_id=obj.id).delete()
                    obj.delete()
                    return JsonResponse({"message": "Eliminado correctamente."}, status=200)

                # Sin tipo: buscar de forma única (riesgo de colisiones si IDs coinciden)
                encontrados = []
                for m in self.MODEL_MAP.values():
                    if m.objects.filter(pk=pk).exists():
                        encontrados.append(m)

                if not encontrados:
                    return JsonResponse({"message": "No existe el documento."}, status=404)
                if len(encontrados) > 1:
                    return JsonResponse(
                        {"message": "Conflicto: el ID existe en más de un tipo. Envía ?tipo=01|03|07|08."},
                        status=409
                    )

                model = encontrados[0]
                obj = get_object_or_404(model, pk=pk)
                ct = ContentType.objects.get_for_model(model)

                DetalleDocumento.objects.filter(content_type=ct, object_id=obj.id).delete()
                Cuota.objects.filter(content_type=ct, object_id=obj.id).delete()
                obj.delete()
                return JsonResponse({"message": "Eliminado correctamente."}, status=200)

        except Exception:
            logger.exception("Error al eliminar documento")
            return JsonResponse({"message": "Error interno al eliminar."}, status=500)