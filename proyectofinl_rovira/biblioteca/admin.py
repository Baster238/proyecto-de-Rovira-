from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from biblioteca.models import Rol, Usuario, Autor, Categoria, Libro, Prestamo


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'created_at')
    search_fields = ('nombre',)


@admin.register(Usuario)
class UsuarioCustomAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Biblioteca', {'fields': ('rol', 'telefono', 'direccion')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Biblioteca', {'fields': ('rol', 'telefono', 'direccion')}),
    )


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'nacionalidad', 'created_at')
    search_fields = ('nombre', 'nacionalidad')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'created_at')
    search_fields = ('nombre',)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'isbn', 'autor', 'categoria', 'stock_disponible', 'stock_total')
    list_filter = ('categoria', 'autor')
    search_fields = ('titulo', 'isbn', 'editorial')


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'libro', 'fecha_prestamo', 'fecha_devolucion_esperada', 'estado')
    list_filter = ('estado', 'fecha_prestamo')
    search_fields = ('usuario__username', 'libro__titulo')
