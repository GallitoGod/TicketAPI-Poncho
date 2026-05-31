import numpy as np
import pandas as pd
from django.utils import timezone
from django.db.models import Sum
from .services import obtener_vistas_youtube


class MotorDinamico:
    
    def __init__(self, ruta, w1, w2, w3, k_pop= 6):
        
        try:
            self.df_artistas = pd.read_csv(ruta)
        except FileNotFoundError:
            raise Exception(f"No se encuentra el archivo .csv en la ruta {ruta}")
        
        # Precalcula el valor de desviacion estandar y la mediana
        log_repros = np.log(self.df_artistas['reproducciones']+1)
        self.mu_pop = np.median(log_repros)
        self.sigma_pop = log_repros.std()
        self.k_pop = k_pop

        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
    
    def coef_popularidad(self, reproducciones_artista) -> float:
        log_x = np.log(reproducciones_artista + 1)
        z = self.k_pop * (log_x - self.mu_pop) / self.sigma_pop
        p = 1 / (1 + np.exp(-z))
        return p

    def coef_tiempo(self, evento) -> float:
        hoy = timezone.now()
        dias_totales = (evento.fecha - evento.preventa).days
        dias_faltantes = (evento.fecha - hoy).days
        dias_faltantes = max(0, dias_faltantes)
        dias_totales = max(1, dias_totales)
        
        x = max(0, min(1, dias_faltantes / dias_totales))
        return (1 - x) ** 2

    def coef_escacez(self, evento) -> float:
        totales = evento.sectorentrada_set.aggregate(
            capacidad = Sum('capacidad_total'),
            vendidas = Sum('entradas_vendidas')
        )

        capacidad = totales['capacidad'] or 1
        vendidas = totales['vendidas'] or 0
        restante = capacidad - vendidas

        porcentaje_disponible = max(0, min(1, restante / capacidad))
        return (1 - porcentaje_disponible) ** 2
    
    def cotizar_ticket(self, evento):
        reproducciones = evento.bkp_reproducciones
        sectores = evento.sectorentrada_set.all()

        c_pop = self.coef_popularidad(reproducciones)
        c_dias = self.coef_tiempo(evento)
        c_escacez = self.coef_escacez(evento)

        precios_finales = []
        for sector in sectores:
    
            precio_f = sector.precio_base_ars + (self.w1 * c_pop) + (self.w2 * c_dias) + (self.w3 * c_escacez)
            precios_finales.append({
                'sector': sector, 
                'precio_ticket': precio_f
            })
    
        return precios_finales