from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from biblioteca.serializers import LoginSerializer, RegisterSerializer, UsuarioSerializer


class LoginAPIView(views.APIView):
    """
    Endpoint para autenticación de usuarios.
    Recibe username y password, y retorna tokens JWT y datos del usuario.
    Regla de seguridad 5: En caso de credenciales inválidas no expone detalles ni si el usuario existe.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = serializer.validated_data['tokens']
            user_data = UsuarioSerializer(user).data
            return Response({
                'mensaje': 'Autenticación exitosa.',
                'tokens': tokens,
                'usuario': user_data
            }, status=status.HTTP_200_OK)

        # Regla 5 / Caso de Prueba 2: Rechazar con 401 sin exponer credenciales
        error_detail = serializer.errors.get('detail')
        if error_detail:
            mensaje = error_detail[0] if isinstance(error_detail, list) else str(error_detail)
        else:
            mensaje = "Credenciales inválidas. Por favor verifique sus datos de acceso."
        return Response({'detail': mensaje}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterAPIView(views.APIView):
    """
    Endpoint para auto-registro de usuarios (rol LECTOR por defecto).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response({
                'mensaje': 'Usuario registrado exitosamente.',
                'usuario': UsuarioSerializer(usuario).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerfilAPIView(views.APIView):
    """
    Endpoint para consultar los datos del usuario actualmente autenticado (Ruta protegida).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
