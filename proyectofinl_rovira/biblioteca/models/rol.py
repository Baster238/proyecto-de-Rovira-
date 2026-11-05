from django.db import models


class Rol(models.Model):
    ADMINISTRADOR = 'ADMINISTRADOR'
    BIBLIOTECARIO = 'BIBLIOTECARIO'
    LECTOR = 'LECTOR'

    ROLES_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (BIBLIOTECARIO, 'Bibliotecario'),
        (LECTOR, 'Lector / Usuario'),
    ]

    nombre = models.CharField(
        max_length=50,
        unique=True,
        choices=ROLES_CHOICES,
        verbose_name="Nombre del Rol"
    )
    descripcion = models.TextField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción"
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
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['id']

    def __str__(self):
        return f"{self.nombre}"
