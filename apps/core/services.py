import requests # Esta libreria basicamente le permite a python que actue como un cliente 
# y pueda pedirle datos a otros servicios. 
from .models import Ticket, Evento
from rest_framework.exceptions import APIException
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
        

"""
    Esta API de abajo sufrio varios cambios desde la idea incial. Resulta que ahora Spotify, para utilizar su API, pide ser
un usuario premium y ya no trae un indice de popularidad, por lo que nos vemos obligados a ir por otro medio. 
    Existe una API llamada Last.fm. La cual a traves de un endpoint publico llamado 'artist.getInfo', pasandole el 
nombre del artista, devuelve un JSON con dos datos utiles: stats.listeners y stats.playcount. El problema es que no es una escala
de popularidad comoda como la de Spotify, daba un numero del 0 al 100 lo que facilitaba todo, esta API da numeros inmensos.
    Por dar un ejemplo, ACDC da 40000000 de oyentes mientras que un aritista de folclore quizas da 15000.
    Lo que quiere decir que si no mastico un poco estos numeros puedo romper el motor de precios con la idea inicial, entonces:

    IDEA DE CONSUMO, USO DE DATOS Y DEFENSA DEL DETERMINISMO:
    Basandome en lo que aprendi del libro "Aprende Machine Learning con Scikit-Learn, Keras y TensorFlow" voy a fundamentar
porque no utilizar machine learning en este caso especifico y porque optar por un algoritmo determinista logaritmico:

    La idea de un algoritmo estocastico como lo puede ser un modelo de regresion cualquiera o arboles de decisiones, necesariamente
utiliza datos historicos, los cuales no tenemos, para hacer predicciones probabilisticas. Entonces esa idea queda descartada, quedando
la idea de algoritmos deterministas. El problema, como escribi arriba, son los datos. Estos vienen en uan distribucion de potencias, 
donde el 1% de los artistas tienen el 90% de las reproducciones (no quiero eso para el motor). Entonces, utilizando la recomendacion
del libro, vamos a manejar estas caracteristicas don distribuciones de cola larga aplicandole una escala logaritmica.
    Basicamente comprimimos valores inmensos, por lo que la distancia entre 1000 y 10000 oyentes es la misma a la que
hay entre 1000000 y 10000000 oyentes. Equilibrando los valores para que pueda andar el motor de precios dinamicos.
"""


def popularidad_artista(evento_id):
    """
        Esto cumple con el RNF-04, para no llamar todo el tiempo la API de last.fm.
        Tambien cumple con el RNF-03 guardando un backup del ultimo dato de popularidad del artista.
    """
    try: 
        evento = Evento.objects.get(id= evento_id)

    except requests.RequestException:
        pass