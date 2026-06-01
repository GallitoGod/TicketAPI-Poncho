import numpy as np
import pandas as pd
from django.utils import timezone
from django.db.models import Sum


class MotorDinamico:
    
    def __init__(self, ruta, k_pop= 6):
        
        try:
            self.df_artistas = pd.read_csv(ruta)
        except FileNotFoundError:
            raise Exception(f"No se encuentra el archivo .csv en la ruta {ruta}")
        
        # Precalcula el valor de desviacion estandar y la mediana
        log_repros = np.log(self.df_artistas['reproducciones']+1)
        self.mu_pop = np.median(log_repros)
        self.sigma_pop = log_repros.std()
        self.k_pop = k_pop

    
    def coef_popularidad(self, reproducciones_artista) -> float:
        log_x = np.log(reproducciones_artista + 1)
        z = self.k_pop * (log_x - self.mu_pop) / self.sigma_pop
        p = 1 / (1 + np.exp(-z))
        return 1 + p

    def coef_tiempo(self, evento) -> float:
        hoy = timezone.localdate()
        dias_totales = (evento.fecha - evento.preventa).days
        dias_faltantes = (evento.fecha - hoy).days
        dias_faltantes = max(0, dias_faltantes)
        dias_totales = max(1, dias_totales)
        
        x = max(0, min(1, dias_faltantes / dias_totales))
        return 1 + (1 - x) ** 2

    def coef_escacez(self, evento) -> float:
        totales = evento.sectores.aggregate(
            capacidad = Sum('capacidad_maxima'),
            vendidas = Sum('entradas_vendidas')
        )

        capacidad = totales['capacidad'] or 1
        vendidas = totales['vendidas'] or 0
        restante = capacidad - vendidas

        porcentaje_disponible = max(0, min(1, restante / capacidad))
        return 1 + (1 - porcentaje_disponible) ** 2
    
    def cotizar_ticket(self, evento, sector):
        reproducciones = evento.bkp_reproducciones

        c_pop = self.coef_popularidad(reproducciones)
        c_dias = self.coef_tiempo(evento)
        c_escacez = self.coef_escacez(evento)

        precio_base = float(sector.precio_base_ars)
        precio_f = precio_base * (.7 + (.1 * c_pop) + (.1 * c_dias) + (.1 * c_escacez))
    
        return precio_f