# Textcort FastAPI Backend

Backend profesional en FastAPI para la plataforma e-commerce Textcort, migrado y mejorado desde Flask.

## Características

✅ **30+ Endpoints** optimizados  
✅ **Autenticación JWT** con contraseñas encriptadas  
✅ **Gestión completa** de productos, usuarios, ventas y gastos  
✅ **Sistema de carrito** en tiempo real  
✅ **Reportes financieros** detallados  
✅ **Estadísticas** de negocio en dashboard  
✅ **Control de acceso** basado en roles (admin/cliente)  
✅ **Validación de datos** con Pydantic  
✅ **Base de datos** MySQL optimizada  

## Instalación

\`\`\`bash
# 1. Clonar o descargar el proyecto
cd fastapi_backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de base de datos

# 5. Iniciar servidor
python main.py
\`\`\`

## API Base URL

\`\`\`
http://localhost:8000
\`\`\`

## Documentación interactiva

\`\`\`
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
\`\`\`

## Estructura de directorios

\`\`\`
fastapi_backend/
├── main.py                 # Punto de entrada
├── config.py              # Configuración
├── database.py            # Conexión BD
├── models/
│   ├── usuario.py
│   ├── producto.py
│   ├── venta.py
│   └── gasto.py
├── schemas/               # Validación Pydantic
│   ├── usuario.py
│   ├── producto.py
│   ├── venta.py
│   └── gasto.py
├── api/routes/            # Endpoints
│   ├── auth.py
│   ├── usuarios.py
│   ├── productos.py
│   ├── categorias.py
│   ├── carrito.py
│   ├── ventas.py
│   ├── gastos.py
│   ├── reportes.py
│   └── estadisticas.py
├── requirements.txt
├── .env.example
└── README.md
\`\`\`

## Endpoints principales

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual
- `POST /api/auth/refresh` - Renovar token

### Productos
- `GET /api/productos/` - Listar productos
- `GET /api/productos/destacados` - Productos destacados
- `GET /api/productos/{id}` - Obtener producto
- `POST /api/productos/` - Crear producto (admin)
- `PUT /api/productos/{id}` - Actualizar producto (admin)
- `DELETE /api/productos/{id}` - Eliminar producto (admin)

### Usuarios
- `GET /api/usuarios/` - Listar usuarios (admin)
- `GET /api/usuarios/{id}` - Obtener usuario
- `PUT /api/usuarios/me` - Actualizar perfil
- `DELETE /api/usuarios/{id}` - Eliminar usuario (admin)

### Carrito
- `GET /api/carrito/` - Obtener carrito
- `POST /api/carrito/agregar` - Agregar producto
- `PUT /api/carrito/actualizar/{clave}/{accion}` - Actualizar cantidad
- `DELETE /api/carrito/eliminar/{clave}` - Eliminar producto
- `POST /api/carrito/vaciar` - Vaciar carrito

### Ventas
- `GET /api/ventas/` - Listar ventas (admin)
- `GET /api/ventas/mis-ventas` - Mis ventas
- `POST /api/ventas/` - Crear venta
- `GET /api/ventas/{id}` - Obtener detalle venta
- `PUT /api/ventas/{id}` - Actualizar venta (admin)
- `DELETE /api/ventas/{id}` - Cancelar venta (admin)

### Gastos
- `GET /api/gastos/` - Listar gastos (admin)
- `POST /api/gastos/` - Crear gasto (admin)
- `PUT /api/gastos/{id}` - Actualizar gasto (admin)
- `DELETE /api/gastos/{id}` - Eliminar gasto (admin)

### Reportes
- `GET /api/reportes/financiero` - Reporte financiero
- `GET /api/reportes/ventas-por-mes` - Ventas por mes
- `GET /api/reportes/productos-top` - Productos más vendidos
- `GET /api/reportes/clientes-top` - Clientes principales
- `GET /api/reportes/stock-bajo` - Productos con stock bajo

### Estadísticas
- `GET /api/estadisticas/dashboard` - Dashboard general
- `GET /api/estadisticas/usuarios` - Estadísticas de usuarios
- `GET /api/estadisticas/productos` - Estadísticas de productos

## Autenticación

Todos los endpoints protegidos requieren un token JWT en el header:

\`\`\`
Authorization: Bearer {token}
\`\`\`

## Base de datos

### Crear tablas automáticamente

Las tablas se crean automáticamente al iniciar el servidor (mediante `Base.metadata.create_all()`).

Para una migración desde Flask:
1. Exportar datos de MySQL Flask
2. Importar en la nueva BD de FastAPI
3. Las tablas son compatibles

## Notas importantes

- Cambiar `SECRET_KEY` en producción
- Configurar `CORS_ORIGINS` según el frontend
- Usar HTTPS en producción
- Implementar rate limiting para endpoints públicos
- Agregar logging más detallado en producción

## Soporte

Para reportar errores o solicitar cambios, contacta al equipo de desarrollo.
\`\`\`

```plaintext file="fastapi_backend/api/__init__.py"
# API Package
