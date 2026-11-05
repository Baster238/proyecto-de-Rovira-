# API REST para el Manejo de un Sistema Bibliotecario

**Módulo / Asignatura:** Utilización de Frameworks para el Desarrollo de Software  
**Docente:** Oscar Alfredo Cruz Rovira  
**Ciclo / Entrega:** Ciclo II 2026 - Semana 16  
**Tecnología:** Python 3.14 / Django 6.1 / Django REST Framework / SimpleJWT  

---

## 1. Descripción del Proyecto

API REST para la administración de un sistema bibliotecario que centraliza la gestión de usuarios, roles, catálogo bibliográfico (autores, categorías y libros) y préstamos/devoluciones de ejemplares. Incorpora autenticación con tokens JWT con tiempo de expiración, control de acceso basado en roles (RBAC), transacciones atómicas para integridad de stock, hash seguro de contraseñas y códigos de respuesta HTTP estandarizados.

---

## 2. Arquitectura y Metodología Aplicada

Siguiendo la metodología impartida en las clases de las Semanas 10 a 14:
- **Estructura Modular:** Modelos (`models/`), serializadores (`serializers/`) y vistas (`views/`) organizados en paquetes independientes.
- **Modelo de Usuario Personalizado (`Usuario`):** Hereda de `AbstractUser` y `UserManager`, vinculado con clave foránea a un modelo `Rol`.
- **Control de Acceso Basado en Roles:**
  - `ADMINISTRADOR`: Acceso total (gestión de usuarios, roles, catálogo y préstamos).
  - `BIBLIOTECARIO`: Gestión completa de catálogo, registro de préstamos y devoluciones.
  - `LECTOR / USUARIO`: Consulta del catálogo y seguimiento exclusivo de sus propios préstamos (`/api/prestamos/mis_prestamos/`).
- **Seguridad en Autenticación:**
  - Algoritmo de hash PBKDF2/SHA-256 (nunca texto plano).
  - En caso de credenciales incorrectas, responde `401 Unauthorized` con mensaje genérico para no revelar si el usuario existe o no (Regla 5).
  - Tokens JWT (`access` y `refresh`) con tiempo de expiración configurable.
- **Reglas de Negocio en Préstamos y Devoluciones:**
  - Control estricto de disponibilidad: se impide prestar libros con stock disponible igual a 0 (`400 Bad Request`).
  - Al registrar un préstamo, se descuenta 1 ejemplar de manera atómica (`transaction.atomic()`).
  - Al registrar una devolución, el préstamo pasa a estado `DEVUELTO`, se guarda la fecha real y el ejemplar recupera su disponibilidad (`stock_disponible += 1`).
  - Protección de integridad referencial: no se permite eliminar libros o autores con registros asociados (`on_delete=models.RESTRICT`).

---

## 3. Requisitos e Instalación

### Requisitos Previos:
- Python 3.10 o superior (probado en Python 3.14).

### Instalación de Dependencias:
```bash
pip install -r requirements.txt
```

---

## 4. Configuración y Puesta en Marcha

### Paso 1: Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 2: Poblar Datos de Prueba (Seed Data)
El proyecto incluye un comando personalizado que carga automáticamente roles, usuarios, categorías, autores, libros y préstamos de demostración:
```bash
python manage.py seed_biblioteca
```

#### Usuarios precargados disponibles para pruebas:
| Rol | Username | Password | Acceso / Capacidades |
|---|---|---|---|
| **Administrador** | `admin` | `Admin1234!` | Acceso total al sistema y gestión de usuarios |
| **Bibliotecario** | `bibliotecario` | `Biblio1234!` | Gestión de catálogo, préstamos y devoluciones |
| **Lector 1** | `lector_juan` | `Lector1234!` | Consulta de catálogo y sus propios préstamos |
| **Lector 2** | `lector_maria` | `Lector1234!` | Consulta de catálogo y sus propios préstamos |

### Paso 3: Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```
La API quedará disponible en: `http://127.0.0.1:8000/api/`  
El panel administrativo de Django en: `http://127.0.0.1:8000/admin/`

---

## 5. Demostración y Evaluación con Postman

Para la evaluación y demostración ante el docente, se incluye el archivo:
📁 **`Postman_Collection_Sistema_Bibliotecario.json`**

Importa este archivo en **Postman** para probar de manera visual e interactiva los **10 Casos de Prueba Obligatorios** y los **7 Flujos de Demostración** solicitados en la guía:

1. **Login válido:** `POST /api/auth/login/` (obtiene token JWT y datos de usuario).
2. **Login inválido:** `POST /api/auth/login/` con clave incorrecta (rechaza con `401` genérico).
3. **Ruta protegida sin token:** `GET /api/auth/me/` sin header Authorization (rechaza con `401`).
4. **Token inválido o expirado:** `GET /api/auth/me/` con token alterado (rechaza con `401`).
5. **Acción sin permiso:** `POST /api/libros/` con token de Lector (rechaza con `403 Forbidden`).
6. **CRUD de libro:** Crear libro como Bibliotecario (`201`), consultar (`200`), actualizar (`200`), y verificar protección contra borrado si tiene préstamos (`400`).
7. **Préstamo válido:** `POST /api/prestamos/` con libro disponible (crea préstamo `201` y descuenta 1 al stock disponible).
8. **Préstamo inválido:** `POST /api/prestamos/` con libro agotado (rechaza con `400 Bad Request` indicando sin ejemplares).
9. **Devolución:** `POST /api/prestamos/<id>/devolver/` (cambia estado a `DEVUELTO` y suma 1 al stock disponible).
10. **Datos inválidos:** Peticiones con campos faltantes o valores erróneos (rechaza con `400 Bad Request`).

---

## 6. Catálogo de Endpoints REST

### Autenticación y Cuentas
- `POST /api/auth/login/`: Iniciar sesión (recibe `username` y `password`, emite token JWT).
- `POST /api/auth/register/`: Registro de nuevos lectores.
- `GET /api/auth/me/`: Obtener datos del usuario autenticado (Protegida).
- `POST /api/auth/refresh/`: Refrescar token de acceso expirado.

### Catálogo
- `GET|POST /api/autores/`: Listar o crear autores.
- `GET|PUT|PATCH|DELETE /api/autores/<id>/`: Detalle, actualización y eliminación de autor.
- `GET|POST /api/categorias/`: Listar o crear categorías.
- `GET|PUT|PATCH|DELETE /api/categorias/<id>/`: Detalle, actualización y eliminación de categoría.
- `GET|POST /api/libros/`: Listar libros (filtros: `?disponible=true`, `?autor=<id>`, `?categoria=<id>`, `?search=<texto>`) o registrar libro.
- `GET|PUT|PATCH|DELETE /api/libros/<id>/`: Detalle, actualización y eliminación de libro.

### Préstamos y Devoluciones
- `GET /api/prestamos/`: Historial general de préstamos (Staff ve todos, Lector ve los suyos).
- `POST /api/prestamos/`: Registrar nuevo préstamo (Valida stock disponible y descuenta ejemplar).
- `GET /api/prestamos/activos/`: Listado de préstamos activos (no devueltos).
- `GET /api/prestamos/mis_prestamos/`: Préstamos del usuario autenticado.
- `POST /api/prestamos/<id>/devolver/`: Registrar devolución de un libro y restituir stock disponible.

### Administración (Solo Rol Administrador)
- `GET|POST /api/usuarios/`: Gestión de usuarios.
- `GET|PUT|PATCH|DELETE /api/usuarios/<id>/`: Modificación o baja de usuario.
- `GET /api/roles/`: Listado de roles del sistema.
