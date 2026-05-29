from numpy import np
from scipy.stats import rankdata
from .models import Evento, SectorEntrada, Ticket


class MotorDinamico:
    
    def __init__(self, w1, w2, w3):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
    
    def coef_popularidad(x):
        return rankdata(x, method='average') / len(x)
    
    def coef_tiempo(x, dias_faltantes, dias_totales_preventa):
        x = max(0, min(1, dias_faltantes / dias_totales_preventa))
        return 1 + ((1 - x) ** 2)

    def coef_escacez(x, entradas_restantes, capacidad_total):
        porcentaje_disponible = max(0, min(1, entradas_restantes / capacidad_total))
        return 1 + ((1 - porcentaje_disponible) ** 2)
    


def calculo_precio():
    pass