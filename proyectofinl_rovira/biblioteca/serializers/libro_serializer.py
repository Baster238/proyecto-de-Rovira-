from rest_framework import serializers
from biblioteca.models import Libro, Autor, Categoria
from .autor_serializer import AutorSerializer
from .categoria_serializer import CategoriaSerializer


class LibroReadSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    disponibilidad = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = [
            'id', 'titulo', 'isbn', 'autor', 'categoria',
            'anio_publicacion', 'editorial', 'stock_total',
            'stock_disponible', 'disponibilidad', 'created_at', 'updated_at'
        ]

    def get_disponibilidad(self, obj):
        if obj.stock_disponible > 0:
            return "DISPONIBLE"
        return "AGOTADO"


class LibroWriteSerializer(serializers.ModelSerializer):
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        source='autor',
        write_only=True,
        required=True
    )
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
        required=True
    )

    class Meta:
        model = Libro
        fields = [
            'id', 'titulo', 'isbn', 'autor_id', 'categoria_id',
            'anio_publicacion', 'editorial', 'stock_total',
            'stock_disponible', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        stock_total = attrs.get('stock_total', getattr(self.instance, 'stock_total', 1))
        stock_disponible = attrs.get('stock_disponible', getattr(self.instance, 'stock_disponible', stock_total))

        if stock_disponible > stock_total:
            raise serializers.ValidationError({
                "stock_disponible": "El stock disponible no puede exceder el stock total de ejemplares."
            })
        if stock_total < 0:
            raise serializers.ValidationError({
                "stock_total": "El stock total no puede ser un número negativo."
            })
        if stock_disponible < 0:
            raise serializers.ValidationError({
                "stock_disponible": "El stock disponible no puede ser un número negativo."
            })
        return attrs
