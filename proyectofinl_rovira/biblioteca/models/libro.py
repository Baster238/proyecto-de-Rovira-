from django.db import models
from django.core.exceptions import ValidationError
from .autor import Autor
from .categoria import Categoria


class Libro(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    autor = models.ForeignKey(
        Autor,
        on_delete=models.RESTRICT,
        related_name="libros",
        verbose_name="Autor"
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.RESTRICT,
        related_name="libros",
        verbose_name="Categoría"
    )
    anio_publicacion = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Año de publicación"
    )
    editorial = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Editorial"
    )
    stock_total = models.PositiveIntegerField(
        default=1,
        verbose_name="Stock Total"
    )
    stock_disponible = models.PositiveIntegerField(
        default=1,
        verbose_name="Stock Disponible"
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
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['titulo']

    def clean(self):
        if self.stock_disponible > self.stock_total:
            raise ValidationError({
                'stock_disponible': 'El stock disponible no puede superar al stock total de ejemplares.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} (Disponibles: {self.stock_disponible}/{self.stock_total})"
