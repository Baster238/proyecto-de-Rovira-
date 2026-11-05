from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from biblioteca.models import Rol, Usuario, Autor, Categoria, Libro, Prestamo


class Command(BaseCommand):
    help = 'Pobla la base de datos con roles, usuarios, categorías, autores, libros y préstamos de prueba.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando carga de datos iniciales (Seed Data)...'))

        # 1. Crear Roles
        roles_data = [
            (Rol.ADMINISTRADOR, 'Administrador con acceso total a usuarios, catálogo y reportes.'),
            (Rol.BIBLIOTECARIO, 'Bibliotecario encargado del catálogo, préstamos y devoluciones.'),
            (Rol.LECTOR, 'Lector con permisos de consulta y seguimiento de sus préstamos.'),
        ]
        roles_map = {}
        for nombre, desc in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc}
            )
            roles_map[nombre] = rol
            accion = 'Creado' if created else 'Existente'
            self.stdout.write(f'  [Rol] {accion}: {nombre}')

        # 2. Crear Usuarios con contraseñas hasheadas
        usuarios_data = [
            {
                'username': 'admin',
                'password': 'Admin1234!',
                'email': 'admin@biblioteca.edu',
                'first_name': 'Carlos',
                'last_name': 'Administrador',
                'telefono': '7001-0001',
                'direccion': 'Oficina Central de Biblioteca',
                'rol': roles_map[Rol.ADMINISTRADOR],
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'bibliotecario',
                'password': 'Biblio1234!',
                'email': 'bibliotecario@biblioteca.edu',
                'first_name': 'Laura',
                'last_name': 'Martínez',
                'telefono': '7002-0002',
                'direccion': 'Módulo de Atención y Préstamos',
                'rol': roles_map[Rol.BIBLIOTECARIO],
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'lector_juan',
                'password': 'Lector1234!',
                'email': 'juan.perez@correo.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'telefono': '7003-0003',
                'direccion': 'Colonia Las Flores, Pasaje 3 #12',
                'rol': roles_map[Rol.LECTOR],
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'lector_maria',
                'password': 'Lector1234!',
                'email': 'maria.lopez@correo.com',
                'first_name': 'María',
                'last_name': 'López',
                'telefono': '7004-0004',
                'direccion': 'Residencial Los Robles, Casa 45',
                'rol': roles_map[Rol.LECTOR],
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        usuarios_map = {}
        for u in usuarios_data:
            username = u['username']
            password = u.pop('password')
            usuario, created = Usuario.objects.get_or_create(
                username=username,
                defaults=u
            )
            if created:
                usuario.set_password(password)
                usuario.save()
                rol_nombre = u["rol"].nombre
                self.stdout.write(f'  [Usuario] Creado: {username} ({rol_nombre})')
            else:
                self.stdout.write(f'  [Usuario] Ya existía: {username}')
            usuarios_map[username] = usuario

        # 3. Categorías
        categorias_data = [
            ('Desarrollo de Software', 'Libros sobre programación, arquitectura, frameworks y buenas prácticas.'),
            ('Ciencia Ficción', 'Obras de anticipación tecnológica y exploración futurista.'),
            ('Literatura Clásica', 'Clásicos universales de la literatura narrativa e hispánica.'),
            ('Historia Universal', 'Ensayos y relatos sobre hitos históricos de la humanidad.'),
        ]
        categorias_map = {}
        for nombre, desc in categorias_data:
            cat, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc}
            )
            categorias_map[nombre] = cat
            accion = 'Creada' if created else 'Existente'
            self.stdout.write(f'  [Categoría] {accion}: {nombre}')

        # 4. Autores
        autores_data = [
            ('Robert C. Martin', 'EE.UU.', 'Conocido como Uncle Bob, referente en patrones de diseño y Clean Code.'),
            ('George Orwell', 'Reino Unido', 'Escritor, periodista y ensayista célebre por sus novelas distópicas.'),
            ('Gabriel García Márquez', 'Colombia', 'Premio Nobel de Literatura 1982, máximo exponente del realismo mágico.'),
            ('Isaac Asimov', 'Rusia / EE.UU.', 'Bioquímico y prolífico escritor de ciencia ficción y divulgación científica.'),
            ('Miguel de Cervantes', 'España', 'Figura cumbre de las letras españolas y autor de Don Quijote.'),
        ]
        autores_map = {}
        for nombre, nac, bio in autores_data:
            autor, created = Autor.objects.get_or_create(
                nombre=nombre,
                defaults={'nacionalidad': nac, 'biografia': bio}
            )
            autores_map[nombre] = autor
            accion = 'Creado' if created else 'Existente'
            self.stdout.write(f'  [Autor] {accion}: {nombre}')

        # 5. Libros
        libros_data = [
            {
                'titulo': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'isbn': '978-0132350884',
                'autor': autores_map['Robert C. Martin'],
                'categoria': categorias_map['Desarrollo de Software'],
                'anio_publicacion': 2008,
                'editorial': 'Prentice Hall',
                'stock_total': 4,
                'stock_disponible': 4,
            },
            {
                'titulo': '1984',
                'isbn': '978-0451524935',
                'autor': autores_map['George Orwell'],
                'categoria': categorias_map['Ciencia Ficción'],
                'anio_publicacion': 1949,
                'editorial': 'Secker & Warburg',
                'stock_total': 3,
                'stock_disponible': 3,
            },
            {
                'titulo': 'Cien Años de Soledad',
                'isbn': '978-0307474728',
                'autor': autores_map['Gabriel García Márquez'],
                'categoria': categorias_map['Literatura Clásica'],
                'anio_publicacion': 1967,
                'editorial': 'Editorial Sudamericana',
                'stock_total': 5,
                'stock_disponible': 5,
            },
            {
                'titulo': 'Don Quijote de la Mancha',
                'isbn': '978-8424116286',
                'autor': autores_map['Miguel de Cervantes'],
                'categoria': categorias_map['Literatura Clásica'],
                'anio_publicacion': 1605,
                'editorial': 'Francisco de Robles',
                'stock_total': 2,
                'stock_disponible': 2,
            },
            {
                'titulo': 'Fundación',
                'isbn': '978-0553293357',
                'autor': autores_map['Isaac Asimov'],
                'categoria': categorias_map['Ciencia Ficción'],
                'anio_publicacion': 1951,
                'editorial': 'Gnome Press',
                'stock_total': 1,
                'stock_disponible': 0,  # Agotado inicialmente para prueba de disponibilidad
            },
        ]

        libros_map = {}
        for l in libros_data:
            isbn = l['isbn']
            libro, created = Libro.objects.get_or_create(
                isbn=isbn,
                defaults=l
            )
            libros_map[isbn] = libro
            accion = 'Creado' if created else 'Existente'
            self.stdout.write(f'  [Libro] {accion}: {libro.titulo} (Disponibles: {libro.stock_disponible}/{libro.stock_total})')

        # 6. Préstamo de ejemplo (para el libro Fundación prestado a lector_maria)
        libro_fundacion = libros_map['978-0553293357']
        if not Prestamo.objects.filter(libro=libro_fundacion, estado=Prestamo.ESTADO_ACTIVO).exists():
            prestamo = Prestamo.objects.create(
                usuario=usuarios_map['lector_maria'],
                libro=libro_fundacion,
                fecha_prestamo=timezone.now() - timedelta(days=2),
                fecha_devolucion_esperada=timezone.now() + timedelta(days=5),
                estado=Prestamo.ESTADO_ACTIVO,
                observaciones='Préstamo inicial de demostración para el libro Fundación (ejemplar agotado).'
            )
            self.stdout.write(f'  [Préstamo] Creado préstamo #{prestamo.id} para demostración de libro agotado.')

        self.stdout.write(self.style.SUCCESS('\n[EXITO] Datos iniciales (Seed Data) cargados exitosamente.'))
        self.stdout.write(self.style.SUCCESS('Usuarios disponibles para pruebas:'))
        self.stdout.write('  - Administrador:   usuario="admin"          password="Admin1234!"')
        self.stdout.write('  - Bibliotecario:   usuario="bibliotecario"  password="Biblio1234!"')
        self.stdout.write('  - Lector 1:        usuario="lector_juan"    password="Lector1234!"')
        self.stdout.write('  - Lector 2:        usuario="lector_maria"   password="Lector1234!"\n')
