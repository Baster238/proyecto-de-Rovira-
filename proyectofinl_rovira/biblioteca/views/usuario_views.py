from rest_framework import viewsets, permissions
from biblioteca.models import Usuario, Rol
from biblioteca.serializers import UsuarioSerializer, RolSerializer
from biblioteca.permissions import IsAdminUserRole, IsBibliotecarioOrAdmin


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Usuarios.
    Restringido exclusivamente a Administradores (Regla 4).
    """
    queryset = Usuario.objects.all().select_related('rol')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUserRole]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'id', 'created_at']


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado y detalle de Roles existentes en el sistema.
    """
    queryset = Rol.objects.all().prefetch_related('usuarios')
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]
