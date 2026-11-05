from rest_framework import permissions
from biblioteca.models.rol import Rol


class IsAdminUserRole(permissions.BasePermission):
    """
    Permite acceso únicamente a usuarios con rol ADMINISTRADOR o superusuarios.
    """
    message = "Acceso denegado: Se requiere rol de Administrador para realizar esta acción."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        return bool(request.user.rol and request.user.rol.nombre == Rol.ADMINISTRADOR)


class IsBibliotecarioOrAdmin(permissions.BasePermission):
    """
    Permite acceso a usuarios con rol BIBLIOTECARIO o ADMINISTRADOR.
    """
    message = "Acceso denegado: Se requiere rol de Bibliotecario o Administrador para realizar esta acción."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        return bool(request.user.rol and request.user.rol.nombre in [Rol.ADMINISTRADOR, Rol.BIBLIOTECARIO])


class IsBibliotecarioOrAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquier usuario autenticado puede consultar (GET, HEAD, OPTIONS).
    Solo BIBLIOTECARIO o ADMINISTRADOR pueden crear, modificar o eliminar registros.
    """
    message = "Acceso denegado: No tiene permisos de Bibliotecario o Administrador para modificar este recurso."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return bool(request.user.rol and request.user.rol.nombre in [Rol.ADMINISTRADOR, Rol.BIBLIOTECARIO])


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permite al dueño del préstamo ver su detalle, y a Administradores/Bibliotecarios acceso total.
    """
    message = "Acceso denegado: No tiene permisos para acceder al préstamo de otro usuario."

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser or (request.user.rol and request.user.rol.nombre in [Rol.ADMINISTRADOR, Rol.BIBLIOTECARIO]):
            return True
        return obj.usuario_id == request.user.id
