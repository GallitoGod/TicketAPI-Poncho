## Arquitectura General
El sistema utiliza Django REST Framework para las operaciones transaccionales clasicas (HTTP/REST) protegiendo las rutas con JWT (JSON Web Tokens). Para la analitica en tiempo real, se implementa Django Channels  WebSockets, permitiendo hacer push de graficos generados por Pandas y Matplotlib directamente a los clientes suscritos.

---

## Setup y configuraciones:
Esta pagina proporciona una guia tecnica completa para configurar el entorno de desarrollo para el proyecto TicketAPI Poncho. Cubre la gestion de dependencias, la configuracion central de Django y la inicializacion de la infraestructura en tiempo real basada en ASGI.

### Inicializacion del entorno
El proyecto se basa en un conjunto específico de bibliotecas de Python para servicios web, análisis de datos y comunicación en tiempo real.

### Instalacion de dependencias
El sistema requiere Python 3.x y las dependencias enumeradas en requirements.txt. Los paquetes incluyen:
* Django & DRF: Core del proyecto y kit de herramientas REST.
* Channels & Daphne: Soporte asincrono para WebSocket.
* SimpleJWT: Autenticacion de Token.
* Data Stack: numpy, pandas, scipy y matplotlib para el motor de precios dinamico y la generacion de graficos en tiempo real.

```bash 
    pip install -r requirements.txt 
```

### Fuentes:

[requirements.txt](https://github.com/GallitoGod/TicketAPI-Poncho/blob/84888343e8ee2672d2d49bab196e34ddfc5ee741/requirements.txt#L2-L14)

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