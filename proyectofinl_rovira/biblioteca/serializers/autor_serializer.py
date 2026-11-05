from rest_framework import serializers
from biblioteca.models import Autor


class AutorSerializer(serializers.ModelSerializer):
    libros_count = serializers.IntegerField(source='libros.count', read_only=True)

    class Meta:
        model = Autor
        fields = ['id', 'nombre', 'nacionalidad', 'biografia', 'libros_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
