from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from biblioteca.views import (
    LoginAPIView,
    RegisterAPIView,
    PerfilAPIView,
    AutorViewSet,
    CategoriaViewSet,
    LibroViewSet,
    PrestamoViewSet,
    UsuarioViewSet,
    RolViewSet,
)

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'autores', AutorViewSet, basename='autor')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'libros', LibroViewSet, basename='libro')
router.register(r'prestamos', PrestamoViewSet, basename='prestamo')

urlpatterns = [
    # Autenticación y Tokens JWT
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/me/', PerfilAPIView.as_view(), name='api-perfil'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),

    # Recursos REST (Router)
    path('', include(router.urls)),
]
