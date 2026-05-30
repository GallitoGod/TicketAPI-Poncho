import requests # Esta libreria basicamente le permite a python que actue como un cliente 
# y pueda pedirle datos a otros servicios. 
from .models import Ticket, Evento
from rest_framework.exceptions import APIException
from dotenv import load_dotenv
import urllib.parse
import os
"""
    APIException es la clase de manejo de errores de Django Rest Framework, 
es mas que nada para que no explote el servidor dandome un error 500, por lo que
puedo dar una respuesta HTTP en formato JSON.
"""

class ServicioCotizacionCaido_SinRegistros(APIException):
    status_code = 503 # Que dice que el servicio esta desabilitado
    default_detail = "El servicio de cotizacion no se encuentra disponible en este momento " \
    "y no hay valores para un calculo correcto. Por favor, intente de nuevo en unos minutos."
    default_code = 'cotizacion_caida'
    """
        El cliente que consuma esta API no va a ver una pantalla de erro, va a ver un JSON asi:
        {"detail": "El servicio de cotizacion no se encuentra disponible en este momento 
    y no hay valores para un calculo correcto. Por favor, intente de nuevo en unos minutos."}
        con un codigo 503 y ahi el propio cliente va a tener que ver como muestra esto.
    """
    # El 500 rompe todo. 500 = malo, no tocar.


def cotizacion_dolar():
    """
        Obtiene la cotizacion del dolar RF-08 y prepara el fallback RNF-03.
    """
    url = "https://dolarapi.com/v1/dolares/blue"
    """
        Esta url es para Argentina, si no le pusiera '/blue' me devolveria un array en donde
    estarian todos los cambios. Como no es el caso y estoy poniendo que solo quiero el blue,
    este es el JSON con el que trabajo:
            {
                "moneda": "USD",
                "casa": "blue",
                "nombre": "Blue",
                "compra": (el numero de compra actual),
                "venta": (el numero de venta actual),
                "fechaActualizacion": (la fecha y hora de estos numeros)
            }
        Donde solo me iteresa el valor de venta, que es el que utilizo abajo.
    """

    try:
        respuesta = requests.get(url, timeout= 3)
        # Esto es basicamente una peticion con tiempo corto para no colgar el backend.
        # Si dolarAPI no me devulve informacion en mas de 3 segundos se corta la comunicacion 
        # y me da error, cayendo en la linea de abajo.
        respuesta.raise_for_status()
        # Esto lanza una excepcion en caso de que el status sea distinto de 200.
        datos = respuesta.json()
        precio_venta = datos.get('venta')

        return precio_venta
    
    except requests.RequestException:
        
        """   Aca se obtiene el ultimo valor de cotizacion a traves de la fecha de transaccion que muestra el ultimo ticket.
            en caso de que la base de datos no tenga nisiquiera estos valores lo mejor seria cancelar toda operacion
            hasta poder volver a establecer comunicacion con la API.
        """
        ultimo_ticket = Ticket.objects.order_by('-fecha_transaccion').first()
        if ultimo_ticket and ultimo_ticket.bkp_precio_USD > 0:
            ultima_cotizacion = ultimo_ticket.precio_final_ars / ultimo_ticket.bkp_precio_USD
            return ultima_cotizacion
        
        return ServicioCotizacionCaido_SinRegistros()
        #   Esto pasa solo cuando la base de datos no tiene registro de ultimas transacciones y al mismo tiempo
        # dolarAPI esta caido, es el peor caso posible y por eso se deberia esperar a volver a tener comunicacion con la API.


def obtener_vistas_youtube(artista):
    load_dotenv()
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    if not API_KEY:
        raise ValueError("NO ANDA LOCOOOOOOOO")
    """
        Esto cumple con el RNF-04, para no llamar todo el tiempo la API de last.fm.
        Tambien cumple con el RNF-03 guardando un backup del ultimo dato de popularidad del artista.

        El JSON que me devuelve el chistoso de YouTube:
        {
            "kind": "youtube#videoListResponse",
            "etag": "ejemplo_etag_string",
            "items": [
                {
                "kind": "youtube#video",
                "etag": "ejemplo_etag_item",
                "id": "VIDEO_ID_AQUI",
                "snippet": {
                    "publishedAt": "2023-10-01T12:00:00Z",
                    "channelId": "CHANNEL_ID_AQUI",
                    "title": "Título del Video",
                    "description": "Descripción completa del video...",
                    "thumbnails": {
                    "default": { "url": "https://...", "width": 120, "height": 90 },
                    "medium": { "url": "https://...", "width": 320, "height": 180 },
                    "high": { "url": "https://...", "width": 480, "height": 360 }
                    },
                    "channelTitle": "Nombre del Canal",
                    "tags": ["tag1", "tag2"],
                    "categoryId": "22"
                },
                "statistics": {
                    "viewCount": "15000",
                    "likeCount": "1200",
                    "favoriteCount": "0",
                    "commentCount": "300"
                }
                }
            ],
            "pageInfo": {
                "totalResults": 1,
                "resultsPerPage": 1
            }
    }
        
    Bien, todo lo que pida va a venir en 'items' es de a donde tengo que sacar todo, 'kind' da el tipo de recurso, 
    'snippet' me da el canal y 'statics' tiene likes y vistas pero esta parte la tengo que solicitar para que me la traiga.

    Entonces, primero voy a buscar el canal del artista, despues voy a ver las estadisticas del canal, entonces por artista
gasto 101 unidades AURA
    """
    nombre_seguro = urllib.parse.quote(artista)
    # Esto convierte espacios o caracteres raros en formato URL seguro

    #El paso 1 era buscar el canal:
    snippet_url = "https://www.googleapis.com/youtube/v3/search"
    snippet_parametros = {
        'part': 'snippet',
        'q': nombre_seguro,
        'type': 'channel',
        'maxResults': 1,
        'key': API_KEY
    }
    try:

        respuesta = requests.get(snippet_url, params= snippet_parametros)
        snippet = respuesta.json()

        if not snippet.get('items'):
            raise requests.RequestException()
        
        channel_id = snippet['items'][0]['snippet']['channelId']

        # Viene el paso dos loco: las estadisticas
        stats_url = "https://www.googleapis.com/youtube/v3/channels"
        stats_parametros = {
            'part': 'statistics',
            'id': channel_id,
            'key': API_KEY
        }

        stats = requests.get(stats_url, stats_parametros)
        stats_data = stats.json()
        vistas_totales = stats_data['items'][0]['statistics']['viewCount']
        return int(vistas_totales)
  

    except requests.RequestException:
        return None