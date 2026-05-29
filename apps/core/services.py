import requests # Esta libreria basicamente le permite a python que actue como un cliente 
# y pueda pedirle datos a otros servicios. 
from .models import Ticket, Evento
from rest_framework.exceptions import APIException
import urllib.parse
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



# API key	    5832f64f725bdc55ec55b8f083929bb6
# Shared secret	3fb747ec1b27c04adaaafbef54042bf2
# Registered to	gallitoGod_1
def oyentes_artista(evento_id):
    api_key = '5832f64f725bdc55ec55b8f083929bb6'
    """
        Esto cumple con el RNF-04, para no llamar todo el tiempo la API de last.fm.
        Tambien cumple con el RNF-03 guardando un backup del ultimo dato de popularidad del artista.

        El JSON que devuelve Last.fm para artist.getinfo tiene esta estructura:
            {
                "artist": {
                    "name": "Cher",
                    "stats": {
                        "listeners": "123456",
                        "playcount": "9876543"
                    },
                    "tags": { ... },
                    "bio": { ... }
                }
            }
        Donde solo interesan los valores dentro de 'stats'.
    """
    try: 
        evento = Evento.objects.get(id= evento_id)
        if evento.artista_principal:

            nombre_seguro = urllib.parse.quote(evento.artista_principal)
            # Esto convierte espacios o caracteres raros en formato URL seguro

            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={nombre_seguro}&api_key={api_key}&format=json&autocorrect=1"
            # Last.fm tiene una funcion para corregir nombres mal tipeados simplemente poniendo en la URL "autocorrect=1"
            # Si alguien escribe "GUNS N ROSES", la propia api lo cambiaria a "GUNS N' ROSES", tambien funciona con tildes.

            respuesta = requests.get(url, timeout= 3)
            respuesta.raise_for_status()
            datos = respuesta.json()
            oyentes = datos.get('artist', {}).get('stats', {}).get('listeners')
            
            return oyentes
        
        else: 
            raise requests.RequestException()

    except requests.RequestException:
        pass