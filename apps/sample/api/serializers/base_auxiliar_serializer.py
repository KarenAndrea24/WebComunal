
from rest_framework import serializers


class BaseAuxiliarSerializer(serializers.ModelSerializer):
    """Serializador simple para catálogos/maestros."""
    class Meta:
        fields = "__all__"
        read_only_fields = ["id"]