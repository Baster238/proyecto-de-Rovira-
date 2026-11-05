from django.db import models
from django.utils import timezone
from .usuario import Usuario
from .libro import Libro


class Prestamo(models.Model):
    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_DEVUELTO = 'DEVUELTO'
    ESTADO_VENCIDO = 'VENCIDO'

    ESTADOS_CHOICES = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_DEVUELTO, 'Devuelto'),
        (ESTADO_VENCIDO, 'Vencido'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.RESTRICT,
        related_name="prestamos",
        verbose_name="Usuario Lector"
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.RESTRICT,
        related_name="prestamos",
        verbose_name="Libro"
    )
    fecha_prestamo = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Préstamo"
    )
    fecha_devolucion_esperada = models.DateTimeField(
        verbose_name="Fecha Esperada de Devolución"
    )
    fecha_devolucion_real = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha Real de Devolución"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_CHOICES,
        default=ESTADO_ACTIVO,
        verbose_name="Estado del Préstamo"
    )
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']

    def __str__(self):
        return f"Préstamo #{self.id} | Libro: {self.libro.titulo} | Usuario: {self.usuario.username} [{self.estado}]"
