from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from biblioteca.models import Usuario, Rol


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, trim_whitespace=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Autenticación segura de Django (verifica hash de contraseña)
        user = authenticate(username=username, password=password)

        # Regla de seguridad 5: No revelar si el usuario existe o no, mensaje genérico
        if not user:
            raise serializers.ValidationError({
                "detail": "Credenciales inválidas. Por favor verifique sus datos de acceso."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "Esta cuenta de usuario se encuentra inactiva o deshabilitada."
            })

        # Generación de token JWT con tiempo de expiración
        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'token_type': 'Bearer',
            }
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        source='rol',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'telefono', 'direccion', 'rol_id'
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Las contraseñas no coinciden."
            })
        if Usuario.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({
                "email": "Ya existe un usuario registrado con este correo electrónico."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        # Asignar rol LECTOR por defecto si no se especifica
        if 'rol' not in validated_data or not validated_data['rol']:
            rol_lector, _ = Rol.objects.get_or_create(
                nombre=Rol.LECTOR,
                defaults={'descripcion': 'Rol de Usuario Lector'}
            )
            validated_data['rol'] = rol_lector

        usuario = Usuario(**validated_data)
        # Hash seguro de contraseña (regla 7 de seguridad)
        usuario.set_password(password)
        usuario.save()
        return usuario
