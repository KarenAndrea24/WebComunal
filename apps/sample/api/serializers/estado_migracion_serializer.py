from rest_framework import serializers

class EstadoMigracionSerializer(serializers.Serializer):
    estado_migracion = serializers.ChoiceField(choices=[
        ('pendiente', 'Pendiente'),
        ('migrado', 'Migrado'),
        ('error_migracion', 'Error de migración'),
    ])
    descripcion_migracion = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['estado_migracion'] == 'error_migracion' and not data.get('descripcion_migracion'):
            raise serializers.ValidationError("Debe proporcionar una descripción si hay error de migración")
        return data
