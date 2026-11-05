from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django.db.models import RestrictedError, Q
from biblioteca.models import Autor, Categoria, Libro
from biblioteca.serializers import (
    AutorSerializer,
    CategoriaSerializer,
    LibroReadSerializer,
    LibroWriteSerializer,
)
from biblioteca.permissions import IsBibliotecarioOrAdminOrReadOnly


class AutorViewSet(viewsets.ModelViewSet):
    """
    CRUD de Autores:
    - Consulta (GET): Cualquier usuario autenticado.
    - Creación, modificación y eliminación: Solo Bibliotecario o Administrador.
    """
    queryset = Autor.objects.all().prefetch_related('libros')
    serializer_class = AutorSerializer
    permission_classes = [IsBibliotecarioOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'nacionalidad']
    ordering_fields = ['nombre', 'created_at']

    def destroy(self, request, *args, **kwargs):
        # Regla 7: Impedir eliminación si compromete integridad referencial
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError:
            return Response(
                {"error": "No se puede eliminar el autor porque tiene libros asociados en el catálogo."},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Categorías:
    - Consulta (GET): Cualquier usuario autenticado.
    - Creación, modificación y eliminación: Solo Bibliotecario o Administrador.
    """
    queryset = Categoria.objects.all().prefetch_related('libros')
    serializer_class = CategoriaSerializer
    permission_classes = [IsBibliotecarioOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created_at']

    def destroy(self, request, *args, **kwargs):
        # Regla 7: Impedir eliminación si compromete integridad referencial
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError:
            return Response(
                {"error": "No se puede eliminar la categoría porque tiene libros asociados en el catálogo."},
                status=status.HTTP_400_BAD_REQUEST
            )


class LibroViewSet(viewsets.ModelViewSet):
    """
    CRUD de Libros:
    - Consulta (GET): Cualquier usuario autenticado.
    - Creación, modificación y eliminación: Solo Bibliotecario o Administrador.
    """
    queryset = Libro.objects.all().select_related('autor', 'categoria')
    permission_classes = [IsBibliotecarioOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'isbn', 'editorial', 'autor__nombre', 'categoria__nombre']
    ordering_fields = ['titulo', 'anio_publicacion', 'stock_disponible', 'created_at']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LibroReadSerializer
        return LibroWriteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro por categoría
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        # Filtro por autor
        autor_id = self.request.query_params.get('autor')
        if autor_id:
            queryset = queryset.filter(autor_id=autor_id)

        # Filtro por disponibilidad
        disponible = self.request.query_params.get('disponible')
        if disponible is not None:
            if disponible.lower() in ['true', '1', 'si']:
                queryset = queryset.filter(stock_disponible__gt=0)
            elif disponible.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(stock_disponible=0)

        return queryset

    def destroy(self, request, *args, **kwargs):
        # Regla 7: Impedir eliminación si compromete integridad referencial (ej: préstamos asociados)
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError:
            return Response(
                {"error": "No se puede eliminar el libro porque cuenta con registros de préstamos históricos o activos asociados."},
                status=status.HTTP_400_BAD_REQUEST
            )
