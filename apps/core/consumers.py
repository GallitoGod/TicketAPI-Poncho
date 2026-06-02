import numpy as np
from django.db.models import Sum
import json
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use('agg') # Esto es para que no me devuelva una ventana directamente como lo hacer matplotlib
import matplotlib.pyplot as plt
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Evento, SectorEntrada, Ticket



def _fig_a_base64(fig):
    """
        Basicamente matplotlib tiene un problema para esto, siempre guarda imagenes en almacenamiento
    lo que es medio pesado para un sistema que tiene que dar respuestas agiles, entonces se guarda la imagen
    en la ram, se la hace base64 y ya se puede cerrar el buffer de ram porque la imagen esta en formato 
    base64 en la variable 'fig_64' y eso lo paso por el tubo del websocket.
    """
    buffer = io.BytesIO() # no almacenamiento
    plt.savefig(buffer, format='png') # lo carga en buffer como png porque es como lo hace matplotlib
    buffer.seek(0) # es como los archivos binarios de C, hay que decirle que vuelva a la posicion 0
    imagen_base64 = base64.b64encode(buffer.read()).decode('utf-8') # base64 es como un algoritmo que pasa 
    # los bits del png a un String raro y utf-8 es un tipo de dato nativo de python para que pueda ser legible
    plt.close(fig) # cierra la figura porque ya esta cargada en fig_64
    buffer.close() # cierra el buffer por lo mismo
    return imagen_base64



class GraficoGlobalConsumer(WebsocketConsumer):

    def connect(self): # Esto se dispara cuando se pide abrir el websocket
        # Se comunica con el propio routing.py a traves del nombre de la clase.

        usuario = self.scope['user']
        if not usuario.is_authenticated or usuario.rol == 'Comprador':
            self.close()

        else:
            self.accept()   
        
            async_to_sync(self.channel_layer.group_add)(
                "estadisticas_admin",
                self.channel_name
            ) # El canal por el que voy a mandr informacion desde ,y hasta, las APIs REST y desde, y asta, esta API

            self.enviar_graficos_globales()

    def disconnect(self, code): # Esto se dispara cuando se deja de usar la url por lo que sea.
        async_to_sync(self.channel_layer.group_discard)(
            "estadisticas_admin",
            self.channel_name
        )# Es para que si nadie autorizado esta viendo la url, no se este mandando datos para nada.

    
    def enviar_graficos_globales(self, event=None):
        
        grf_valor_dinamico = self._generar_grafico_valor_dinamico()
        grf_historico = self._generar_grafico_historico()

        if not grf_valor_dinamico or not grf_historico:
            return

        self.send(text_data=json.dumps({
            'tipo': 'actualizacion_global',
            'img_impacto_b64': grf_valor_dinamico,
            'img_historico_b64': grf_historico
        }))

    def _generar_grafico_valor_dinamico(self):
        """
            Esto costo. Basicamente con aggregate no podia hacer nada porque
        aggregate me devuleve un diccionario con todos los valores acoplados, pero
        annotate me devuelve la sumatoria de todos los valores de cada sector, no me
        acopla todo en un unico dato por evento, sino que cada evento tiene tiene cada sector
        por separado con la suma de todos sus valores.
        """
        eventos = Evento.objects.annotate(
            rec_dinamica=Sum('sectores__tickets__precio_final_ars'),
            rec_estatica=Sum('sectores__precio_base_ars')
        )
        
        if not eventos:
            return None

        nombres = []
        dinamica = []
        estatica = []
        for evento in eventos:
            nombres.append(evento.artista_principal)
            dinamica.append(evento.rec_dinamica or 0)
            estatica.append(evento.rec_estatica or 0)

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(nombres))
        ancho = 0.35

        ax.bar(x - ancho/2, estatica, ancho, label='Recaudacion fija', color='lightgray')
        ax.bar(x + ancho/2, dinamica, ancho, label='Reacaudacion dinamica', color='seagreen')

        ax.set_title('Ganancias de precios dinamicos')
        ax.set_ylabel('Pesos argentinos')
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, rotation=15, ha='right')
        ax.legend()
        plt.tight_layout()

        return _fig_a_base64(fig)

    def _generar_grafico_historico(self):
        
        tickets_or = Ticket.objects.all().order_by('fecha_transaccion').values(
            'sector_entrada__evento__artista_principal', 
            'precio_final_ars'
        )
        
        if not tickets_or:
            return None

        df_tickets = pd.DataFrame(list(tickets_or))
        df_tickets = df_tickets.rename(columns={
            'sector_entrada__evento__artista_principal': 'evento', 
            'precio_final_ars': 'precio_pagado'
        })

        fig, ax = plt.subplots(figsize=(10, 6))
        
        for nombre_evento, df_grupo in df_tickets.groupby('evento'):
            df_grupo = df_grupo.reset_index(drop=True)
            df_grupo.index += 1
            
            recaudacion_acumulada = df_grupo['precio_pagado'].cumsum()
            
            ax.plot(df_grupo.index, recaudacion_acumulada, linewidth=2.5, label=f'{nombre_evento}')

        ax.set_title('Historial de ganancias sobre ventas')
        ax.set_xlabel('Ventas')
        ax.set_ylabel('Ganancias')
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.7)
        plt.tight_layout()

        return _fig_a_base64(fig)




class GraficoConsumer(WebsocketConsumer):

    def connect(self):
        usuario = self.scope['user']
        if not usuario.is_authenticated or usuario.rol == 'Comprador':
            self.close()

        else:
            self.evento_id = self.scope['url_route']['kwargs']['evento_id']
            """
                scope es el request de Django CRUD, tiene el usuario la url y otras cosas.
                Desde url puedo entrar a los parametros de la url que es 'kwargs' y de ahi
            llego a el 'evento_id'.
            """
            self.room_name = f'evento_{self.evento_id}'
            #   Estos canales, le llaman habitaciones o grupos, se usan para el cambio de sincronico a asincronico
            # o viceversa, ya que entre ellos no se entienden.

            async_to_sync(self.channel_layer.group_add)( # Con group_add entro al usuario a la habitacion.
                self.room_name, # Esto es mio.
                self.channel_name # Esto es de django.
            )# Esta es la funcion con la que puedo comunicar las APIs REST con esta API
            self.accept()

            self.enviar_graficos_especificos()

    def disconnect(self, code): # Lo mismo con esta funcion, toda de django, no me hago cargo, jujuuu rima.
        async_to_sync(self.channel_layer.group_discard)( # Con group_discard quito el usuario de la sala.
            self.room_name,
            self.channel_name
        )

    def enviar_graficos_especificos(self, event=None):
            grf_sectores = self._generar_grafico_sectores()

            if not grf_sectores:
                return None

            self.send(text_data=json.dumps({
                'tipo': 'actualizacion_sectores',
                'imagen_b64': grf_sectores
            }))# Esto es lo que manda como JSON las cosas que le cargo al cliente. 
            #   Por eso necesitaba que sea un String legible.


    def _generar_grafico_sectores(self):
        sectores = SectorEntrada.objects.filter(evento_id=self.evento_id)
        
        if not sectores:
            return

        nombres = []
        vendidas = []
        disponibles = []
        for sector in sectores:
            nombres.append(sector.nombre_sector)
            vendidas.append(sector.entradas_vendidas)
            disponibles.append(sector.capacidad_maxima - sector.entradas_vendidas)

        fig, ax = plt.subplots(figsize=(8, 4))
        
        ax.barh(nombres, vendidas, color='tomato', label='Vendidas')
        ax.barh(nombres, disponibles, left=vendidas, color='lightgray', label='Disponibles')
        
        ax.set_title(f'Escasez por sector')
        ax.set_xlabel('Cantidad de entradas')
        ax.legend()
        plt.tight_layout()

        return _fig_a_base64(fig)