from datetime import timedelta
from types import SimpleNamespace
import pytest
from django.utils import timezone

"""
Que se testea en este script:
  - Si un coeficiente se va de rango, todos los precios salen mal.
  - Verifico INVARIANTES avisa si la formula deja de tener sentido.

Coeficientes esperados (segun la formula del codigo):
  - coef_popularidad: sigmoide -> siempre en (1, 2), crece con reproducciones.
  - coef_tiempo:      1 (falta mucho), 2 (es hoy/ya paso).
  - coef_escasez:     1 (vacio), 2 (lleno).
  - cotizar_ticket:   precio_base * (0.7 + 0.1*cpop + 0.1*cdias + 0.1*cesc).
"""

#   coef_popularidad: no uso la base de datos
def test_coef_popularidad_dentro_de_rango(motor):   # 'motor' viene del fixture
    # Para cualquier cantidad de reproducciones: [1, 2].
    # en los extremos el sigmoide satura a 1.0 / 2.0
    for repros in [0, 1_000, 1_000_000, 5_000_000_000]:
        c = motor.coef_popularidad(repros)
        assert 1.0 <= c <= 2.0


def test_coef_popularidad_crece_con_reproducciones(motor):
    # Un artista mas escuchado debe ser mas caro que uno chico.
    poco = motor.coef_popularidad(10_000)
    mucho = motor.coef_popularidad(5_000_000_000)
    assert mucho > poco


#   coef_tiempo: solo usa evento.fecha y evento.preventa entonces 
#   uso SimpleNamespace que es simplemente, que redundante, un "objeto" falso
def test_coef_tiempo_evento_lejano_cercano_a_uno(motor):
    hoy = timezone.localdate()
    evento = SimpleNamespace(preventa=hoy, fecha=hoy + timedelta(days=100))
    c = motor.coef_tiempo(evento)
    assert 1.0 <= c < 1.1  # falta mucho, casi sin subida en el rango


def test_coef_tiempo_evento_inminente_cercano_a_dos(motor):
    hoy = timezone.localdate()
    evento = SimpleNamespace(preventa=hoy - timedelta(days=30), fecha=hoy)
    c = motor.coef_tiempo(evento)
    assert c == pytest.approx(2.0)  # esta muy cerca del valor maximo del rango


#   coef_escasez:  necesita DB entonces los traigo del fixture
def test_coef_escasez_sin_ventas_cercano_a_uno(motor, evento, sector):
    # sector arranca con 0 vendidas,casi todo disponible, coef ~ 1.
    c = motor.coef_escasez(evento)
    assert c == pytest.approx(1.0)


def test_coef_escasez_agotado_cercano_a_dos(motor, evento, sector):
    sector.entradas_vendidas = sector.capacidad_maxima  # 100% vendido
    sector.save()
    c = motor.coef_escasez(evento)
    assert c == pytest.approx(2.0)


#   cotizar_ticket: con los 3 coeficientes 
def test_cotizar_ticket_respeta_la_formula(motor, evento, sector):
    precio = motor.cotizar_ticket(evento, sector)
    base = float(sector.precio_base_ars)

    # Con coefs en (1,2): factor en (1.0, 1.3).
    assert base * 1.0 < precio < base * 1.3


def test_cotizar_ticket_mas_caro_si_esta_agotado(motor, evento, sector):
    precio_vacio = motor.cotizar_ticket(evento, sector)
    sector.entradas_vendidas = sector.capacidad_maxima
    sector.save()
    precio_lleno = motor.cotizar_ticket(evento, sector)
    assert precio_lleno > precio_vacio


def test_csv_inexistente_lanza_excepcion():
    from apps.core.engine import MotorDinamico
    with pytest.raises(Exception):
        MotorDinamico(ruta="no_hay.csv")
