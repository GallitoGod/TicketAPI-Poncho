## Arquitectura General
El sistema utiliza Django REST Framework para las operaciones transaccionales clasicas (HTTP/REST) protegiendo las rutas con JWT (JSON Web Tokens). Para la analitica en tiempo real, se implementa Django Channels  WebSockets, permitiendo hacer push de graficos generados por Pandas y Matplotlib directamente a los clientes suscritos.

---

## 1. Autenticacion y Seguridad

Todas las transacciones de compra requieren estar autenticado. El sistema utiliza tokens de acceso.

### Obtener Token JWT
* Endpoint: `/api/token/`
* Metodo: `POST`
* Descripcion: Intercambia credenciales validas por un Bearer Token.

## 2. APIs REST para CRUD

Los objetos dentro del sistema pueden ser creados, vistos, editados y borrados a traves de las APIs respectivas:

### 1: Eventos
* Endpoint: `/index/evento/`
* Metodos disponibles: GET, POST, PUT, PATCH, DELETE.
* Descripcion: Un CRUD completo para el objeto evento.

### 2: Sectores
* Endpoint: `/index/sectorEntrada/`
* Metodos disponibles: GET, POST, PUT, PATCH, DELETE.
* Descripcion: Un CRUD completo para el objeto sector.

### 3: Tickets
* Endpoint: `/index/ticket/`
* Metodos disponibles: GET, POST, DELETE.
* Descripcion: Un CRUD, sin capacidad de edicion, para el objeto ticket.

### 4: Usuarios
* Endpoint: `/index/usuario/`
* Metodos disponibles: GET, POST, PUT, PATCH, DELETE.
* Descripcion: Un CRUD completo para el objeto usuario.

## 3. API WebSocket para visualizacion de datos:

Las transacciones de compras de tickets en distintos eventos y sectores pueden ser visualizadas a traves de estas API:

* Endpoint: `/ws/dashboard/global/`
* Acceso permitido solo a soporte y produccion.