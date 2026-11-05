from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from biblioteca.models import Prestamo, Libro, Usuario
from .libro_serializer import LibroReadSerializer
from .usuario_serializer import UsuarioSerializer


class PrestamoListSerializer(serializers.ModelSerializer):
    libro = LibroReadSerializer(read_only=True)
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Prestamo
        fields = [
            'id', 'usuario', 'libro', 'fecha_prestamo',
            'fecha_devolucion_esperada', 'fecha_devolucion_real',
            'estado', 'observaciones', 'created_at', 'updated_at'
        ]


class PrestamoCreateSerializer(serializers.ModelSerializer):
    libro_id = serializers.PrimaryKeyRelatedField(
        queryset=Libro.objects.all(),
        source='libro',
        write_only=True,
        required=True
    )
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='usuario',
        write_only=True,
        required=False
    )
    fecha_devolucion_esperada = serializers.DateTimeField(required=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Prestamo
        fields = [
            'id', 'libro_id', 'usuario_id', 'fecha_devolucion_esperada',
            'observaciones', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_fecha_devolucion_esperada(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "La fecha esperada de devolución debe ser posterior a la fecha y hora actual."
            )
        return value

    def validate(self, attrs):
        libro = attrs.get('libro')

        # Regla de negocio 1: No se puede prestar un libro sin disponibilidad
        if libro.stock_disponible <= 0:
            raise serializers.ValidationError({
                "libro": "El libro seleccionado no cuenta con ejemplares disponibles para préstamo."
            })
        return attrs

    def create(self, validated_data):
        # Determinar usuario: si no viene en el payload, usar el usuario autenticado
        request = self.context.get('request')
        if 'usuario' not in validated_data and request and request.user.is_authenticated:
            validated_data['usuario'] = request.user

        libro = validated_data['libro']

        with transaction.atomic():
            # Bloquear fila de libro para evitar condiciones de carrera en concurrencia
            libro_locked = Libro.objects.select_for_update().get(pk=libro.pk)
            if libro_locked.stock_disponible <= 0:
                raise serializers.ValidationError({
                    "libro": "El libro seleccionado se ha agotado durante la solicitud."
                })

            # Descontar 1 ejemplar del stock disponible
            libro_locked.stock_disponible -= 1
            libro_locked.save(update_fields=['stock_disponible', 'updated_at'])

            prestamo = Prestamo.objects.create(
                usuario=validated_data['usuario'],
                libro=libro_locked,
                fecha_devolucion_esperada=validated_data['fecha_devolucion_esperada'],
                observaciones=validated_data.get('observaciones', ''),
                estado=Prestamo.ESTADO_ACTIVO
            )

        return prestamo


class DevolucionSerializer(serializers.Serializer):
    observaciones = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        prestamo = self.context.get('prestamo')
        if not prestamo:
            raise serializers.ValidationError({"detail": "Préstamo no encontrado."})

        # Regla de negocio: validar que no esté ya devuelto
        if prestamo.estado == Prestamo.ESTADO_DEVUELTO:
            raise serializers.ValidationError({
                "detail": "Este préstamo ya ha sido registrado como DEVUELTO con anterioridad."
            })
        return attrs

    def save(self):
        prestamo = self.context.get('prestamo')
        observaciones_nuevas = self.validated_data.get('observaciones', '')

        with transaction.atomic():
            prestamo_locked = Prestamo.objects.select_for_update().get(pk=prestamo.pk)
            libro_locked = Libro.objects.select_for_update().get(pk=prestamo_locked.libro.pk)

            # Actualizar estado del préstamo
            prestamo_locked.estado = Prestamo.ESTADO_DEVUELTO
            prestamo_locked.fecha_devolucion_real = timezone.now()
            if observaciones_nuevas:
                if prestamo_locked.observaciones:
                    prestamo_locked.observaciones += f" | Devolución: {observaciones_nuevas}"
                else:
                    prestamo_locked.observaciones = f"Devolución: {observaciones_nuevas}"
            prestamo_locked.save()

            # Regla de negocio 3: Al registrar una devolución, el libro vuelve a estar disponible
            if libro_locked.stock_disponible < libro_locked.stock_total:
                libro_locked.stock_disponible += 1
                libro_locked.save(update_fields=['stock_disponible', 'updated_at'])

        return prestamo_locked
