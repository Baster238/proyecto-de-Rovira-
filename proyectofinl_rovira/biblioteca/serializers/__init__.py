from .auth_serializer import LoginSerializer, RegisterSerializer
from .rol_serializer import RolSerializer
from .usuario_serializer import UsuarioSerializer
from .autor_serializer import AutorSerializer
from .categoria_serializer import CategoriaSerializer
from .libro_serializer import LibroReadSerializer, LibroWriteSerializer
from .prestamo_serializer import PrestamoListSerializer, PrestamoCreateSerializer, DevolucionSerializer

__all__ = [
    'LoginSerializer',
    'RegisterSerializer',
    'RolSerializer',
    'UsuarioSerializer',
    'AutorSerializer',
    'CategoriaSerializer',
    'LibroReadSerializer',
    'LibroWriteSerializer',
    'PrestamoListSerializer',
    'PrestamoCreateSerializer',
    'DevolucionSerializer',
]
