from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def inicio_view(request):
    return render(request, 'inicio.html')


urlpatterns = [
    # Página principal interactiva con documentación y accesos directos
    path('', inicio_view, name='inicio'),
    path('admin/', admin.site.urls),
    path('api/', include('biblioteca.urls')),
    # Login para la interfaz navegable de DRF en navegador
    path('api-auth/', include('rest_framework.urls')),
]
