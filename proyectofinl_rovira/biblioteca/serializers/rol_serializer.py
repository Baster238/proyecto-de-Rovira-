from rest_framework import serializers
from biblioteca.models import Rol


class RolSerializer(serializers.ModelSerializer):
    usuarios_count = serializers.IntegerField(source='usuarios.count', read_only=True)

    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'usuarios_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
