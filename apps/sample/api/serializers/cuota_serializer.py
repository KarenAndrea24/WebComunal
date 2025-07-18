from rest_framework import serializers
from apps.sample.models.cuota import Cuota

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = [
            'id',
            'fecha',
            'porcentaje',
            'total'
        ]
