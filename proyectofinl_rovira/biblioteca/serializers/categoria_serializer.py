from rest_framework import serializers
from biblioteca.models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    libros_count = serializers.IntegerField(source='libros.count', read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'libros_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
