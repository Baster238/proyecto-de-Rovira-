from django.db import models


class Autor(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre completo")
    nacionalidad = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nacionalidad")
    biografia = models.TextField(null=True, blank=True, verbose_name="Biografía")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
