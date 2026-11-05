from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from .rol import Rol


class UsuarioManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Asignar rol Administrador automáticamente si no se define
        rol_admin, _ = Rol.objects.get_or_create(
            nombre=Rol.ADMINISTRADOR,
            defaults={'descripcion': 'Rol de Administrador con acceso total al sistema'}
        )
        extra_fields.setdefault('rol', rol_admin)

        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    objects = UsuarioManager()

    rol = models.ForeignKey(
        Rol,
        on_delete=models.RESTRICT,
        related_name="usuarios",
        verbose_name="Rol"
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Teléfono"
    )
    direccion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Dirección"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'rol']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['id']

    def __str__(self):
        nombre_completo = f"{self.first_name} {self.last_name}".strip()
        if not nombre_completo:
            nombre_completo = self.username
        rol_nombre = self.rol.nombre if self.rol else 'Sin Rol'
        return f"{nombre_completo} ({self.username}) - {rol_nombre}"
