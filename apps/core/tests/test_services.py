import pytest
import requests
from apps.core import services
from types import SimpleNamespace
"""
Que se testea aca:
  - Hay qye comprobar que la logica reacciona bien a
    cada respuesta (exito, lista vacia, timeout, etc.).
  - Esto es dificl de probar a mano em produccion.
"""

def _explotar(*a, **k):
        # Esta funcion tiene que hacer explotar el codigo con un error de requests
        # por eso necesita esos parametros.
        raise requests.RequestException()

def test_cotizacion_dolar_exito(monkeypatch):
    respuesta_falsa = SimpleNamespace(
        json=lambda: {"venta": 1450},
        raise_for_status=lambda: None
    )

    monkeypatch.setattr(services.requests, "get", lambda *args, **kwargs: respuesta_falsa)
    assert services.cotizacion_dolar() == 1450


@pytest.mark.django_db
def test_cotizacion_dolar_fallback_usa_ultimo_ticket(monkeypatch, sector, comprador):
    from apps.core.models import Ticket
    Ticket.objects.create(
        usuario= comprador, 
        sector_entrada=sector, 
        cantidad=1,
        precio_final_ars= 2000.00, 
        bkp_precio_USD= 2.0
    )
    monkeypatch.setattr(services.requests, "get", _explotar)
    assert services.cotizacion_dolar() == 1000.0


@pytest.mark.django_db
def test_cotizacion_dolar_sin_api_ni_tickets(monkeypatch):
    monkeypatch.setattr(services.requests, "get", _explotar)
    resultado = services.cotizacion_dolar()
    assert isinstance(resultado, services.ServicioCotizacionCaido_SinRegistros)


def tests_youtube_exito(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "FAKE_KEY")
    resp_busqueda = SimpleNamespace(
        json= lambda: {"items": [{"snippet": {"channelId": "CH123"}}]},
        raise_for_status= lambda: None
    )
    resp_stats = SimpleNamespace(
        json = lambda: {"items": [{"statistics": {"viewCount": "15000"}}]},
        raise_for_status = lambda: None
    )
    respuestas = [resp_busqueda, resp_stats]
    def mock_get_explicito(url, params=None):
        return respuestas.pop(0)
    monkeypatch.setattr(services.requests, "get", mock_get_explicito)
    assert services.obtener_vistas_youtube("Soledad Pastorutti") == 15000