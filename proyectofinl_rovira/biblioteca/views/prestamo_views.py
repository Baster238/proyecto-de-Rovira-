from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from biblioteca.models import Prestamo, Rol
from biblioteca.serializers import (
    PrestamoListSerializer,
    PrestamoCreateSerializer,
    DevolucionSerializer,
)
from biblioteca.permissions import IsBibliotecarioOrAdmin, IsOwnerOrStaff


class PrestamoViewSet(viewsets.ModelViewSet):
    """
    Controlador de Préstamos y Devoluciones:
    - Crear préstamo: Requiere rol de Bibliotecario o Administrador.
    - Devolver préstamo: Requiere rol de Bibliotecario o Administrador.
    - Listar: Bibliotecario y Administrador ven todos; Lector ve solo los suyos.
    """
    queryset = Prestamo.objects.all().select_related('libro', 'usuario', 'libro__autor', 'libro__categoria')

    def get_serializer_class(self):
        if self.action in ['create']:
            return PrestamoCreateSerializer
        elif self.action in ['devolver']:
            return DevolucionSerializer
        return PrestamoListSerializer

    def get_permissions(self):
        if self.action in ['create', 'devolver']:
            return [IsBibliotecarioOrAdmin()]
        elif self.action in ['retrieve']:
            return [IsOwnerOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Si el usuario es superuser, admin o bibliotecario, ve todos los préstamos
        if user.is_superuser or (user.rol and user.rol.nombre in [Rol.ADMINISTRADOR, Rol.BIBLIOTECARIO]):
            # Filtro opcional por estado: ?estado=ACTIVO
            estado = self.request.query_params.get('estado')
            if estado:
                queryset = queryset.filter(estado=estado.upper())
            # Filtro opcional por usuario: ?usuario=<id>
            usuario_id = self.request.query_params.get('usuario')
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)
            return queryset

        # Si es un lector regular, únicamente puede ver sus propios préstamos
        return queryset.filter(usuario=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            prestamo = serializer.save()
            # Retornar el detalle serializado completo
            response_serializer = PrestamoListSerializer(prestamo)
            return Response({
                'mensaje': 'Préstamo registrado exitosamente. Stock del libro actualizado.',
                'prestamo': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsBibliotecarioOrAdmin])
    def devolver(self, request, pk=None):
        """
        Endpoint: POST /api/prestamos/<id>/devolver/
        Registra la devolución del libro y repone su disponibilidad.
        """
        prestamo = self.get_object()
        serializer = DevolucionSerializer(
            data=request.data,
            context={'prestamo': prestamo, 'request': request}
        )
        if serializer.is_valid():
            prestamo_actualizado = serializer.save()
            return Response({
                'mensaje': 'Devolución registrada exitosamente. El ejemplar vuelve a estar disponible.',
                'prestamo': PrestamoListSerializer(prestamo_actualizado).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Endpoint: GET /api/prestamos/activos/
        Lista únicamente los préstamos en estado ACTIVO.
        """
        queryset = self.get_queryset().filter(estado=Prestamo.ESTADO_ACTIVO)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PrestamoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PrestamoListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def historial(self, request):
        """
        Endpoint: GET /api/prestamos/historial/
        Lista todos los préstamos históricos.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PrestamoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PrestamoListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_prestamos(self, request):
        """
        Endpoint: GET /api/prestamos/mis_prestamos/
        Permite a cualquier usuario autenticado consultar exclusivamente sus propios préstamos.
        """
        queryset = Prestamo.objects.filter(usuario=request.user).select_related(
            'libro', 'usuario', 'libro__autor', 'libro__categoria'
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PrestamoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PrestamoListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
