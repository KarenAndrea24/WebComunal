from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd


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


class CargaMasivaView(View):
    template_name = 'carga_masiva.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        cabecera_file = request.FILES.get("cabecera")
        detalle_file = request.FILES.get("detalle")
        cuotas_file = request.FILES.get("cuotas")

        # Validación rápida
        if not (cabecera_file and detalle_file and cuotas_file):
            return JsonResponse({"error": "Archivos incompletos"}, status=400)

        # Leer archivos con pandas
        cabecera_df = pd.read_excel(cabecera_file)
        detalle_df = pd.read_excel(detalle_file)
        cuotas_df = pd.read_excel(cuotas_file)

        # Convertir a dict para mostrar en frontend
        return JsonResponse({
            "cabecera": cabecera_df.to_dict(orient='records'),
            "detalle": detalle_df.to_dict(orient='records'),
            "cuotas": cuotas_df.to_dict(orient='records'),
        })
