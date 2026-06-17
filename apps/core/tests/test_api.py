import pytest
from apps.core import views
from apps.core.models import Ticket, SectorEntrada

"""
Que se testea aca:
  - El flujo: routing + permisos + serializer + view + efectos que genera
    Como que si lo usara un cliente realmente.
  - Moneo las apis YouTube y dolar porque la view los llama en perform_create.
  - Uso force_authenticate (no login JWT) porque el jwt lo pruebo en los test de la 
    app Usuario.
"""

pytestmark = pytest.mark.django_db


EVENTO_URL = "/index/evento/"
TICKET_URL = "/index/ticket/"


def test_listar_eventos_es_publico(api_client, evento):
    # GET esta permitido incluso sin autenticar.
    resp = api_client.get(EVENTO_URL)
    assert resp.status_code == 200


def test_comprador_no_puede_crear_evento(api_client, comprador):
    api_client.force_authenticate(user=comprador)
    resp = api_client.post(EVENTO_URL, {
        "nombre": "Recital", 
        "descripcion": "d", 
        "artista_principal": "Luck Ra",
        "preventa": "2030-01-01", 
        "fecha": "2030-02-01", 
        "lugar": "Catamarca",
    })
    assert resp.status_code == 403  # forbiden, te fuiste testeado pa


def test_productor_crea_evento_ok(api_client, productor, monkeypatch):
    api_client.force_authenticate(user=productor)
    #   Devuelve reproducciones sin usar la API real.
    monkeypatch.setattr(views, "obtener_vistas_youtube", lambda artista: 123_456)
    #   monkeypathc literalmente es eso, un parche de mono (o br),le dice a las views
    # que cuando llame a "obtener_vistas_youtube" utilize el lambda.
    resp = api_client.post(EVENTO_URL, {
        "nombre": "Recital", 
        "descripcion": "d", 
        "artista_principal": "Luck Ra",
        "preventa": "2030-01-01", 
        "fecha": "2030-02-01", 
        "lugar": "Catamarca",
    })
    assert resp.status_code == 201, resp.data
    # bkp_reproducciones debe guardarse con lo que devolvio el mono
    assert resp.data["bkp_reproducciones"] == 123_456


def test_productor_evento_artista_invalido(api_client, productor, monkeypatch):
    api_client.force_authenticate(user=productor)
    #   si YouTube no encuentra el canal, services devuelve None, entonces la view
    # responde 400 con ValidationError.
    monkeypatch.setattr(views, "obtener_vistas_youtube", lambda artista: None)

    resp = api_client.post(EVENTO_URL, {
        "nombre": "Recital", 
        "descripcion": "d", 
        "artista_principal": "Chocolate Cheap Charly", # que mandan chaaat
        "preventa": "2030-01-01", 
        "fecha": "2030-02-01", 
        "lugar": "Jupiter",
    })
    assert resp.status_code == 400
    # Ahora que me doy cuenta tendria que cambiar el error y explicarlo.
    # Bueno, queda para una proxima iteracion (no va a haber proxima iteracion)
    assert "artista_principal" in resp.data


def test_comprar_ticket_descuenta_stock(api_client, comprador, sector, monkeypatch):
    api_client.force_authenticate(user=comprador)
    # Aguanten los monos
    monkeypatch.setattr(views, "cotizacion_dolar", lambda: 1000)
    monkeypatch.setattr(views.motor, "cotizar_ticket", lambda evento, s: 5000.0)

    resp = api_client.post(TICKET_URL, {
        "sector_entrada": str(sector.uuid), 
        "cantidad": 2,
    })
    assert resp.status_code == 201, resp.data

    #   el sector debe quedar con 2 entradas vendidas.
    # si no uso refresh_from_db no se actualiza y me devuelve error
    sector.refresh_from_db()
    assert sector.entradas_vendidas == 2

    # Precio final = precio_unitario(5000) * cantidad(2).
    ticket = Ticket.objects.get(uuid=resp.data["uuid"])
    assert ticket.precio_final_ars == 10000.00
    assert ticket.usuario == comprador  # se asigna el usuario logueado


def test_comprar_ticket_requiere_autenticacion(api_client, sector):
    # TicketViewSet exige IsAuthenticated, entonces un anonimo no puede comprar.
    resp = api_client.post(TICKET_URL, {
        "sector_entrada": str(sector.uuid), 
        "cantidad": 1,
    })
    assert resp.status_code in (401, 403)


def test_comprar_mas_que_la_capacidad_falla(api_client, comprador, evento, monkeypatch):
    api_client.force_authenticate(user=comprador)
    monkeypatch.setattr(views, "cotizacion_dolar", lambda: 1000)
    monkeypatch.setattr(views.motor, "cotizar_ticket", lambda evento, s: 5000.0)

    chico = SectorEntrada.objects.create(
        evento=evento, 
        nombre_sector="VIP", 
        capacidad_maxima=2,
        entradas_vendidas=0, 
        precio_base_ars=10000,
    )
    # cantidad valida por transaccion (<=4) pero supera la capacidad (2)
    resp = api_client.post(TICKET_URL, {
        "sector_entrada": str(chico.uuid), 
        "cantidad": 3,
    })
    assert resp.status_code == 400


def test_ticket_no_permite_put(api_client, comprador, sector):
    # La view limita los verbos de actualizacion para los tickets.
    api_client.force_authenticate(user=comprador)
    resp = api_client.put(f"{TICKET_URL}algo/", {"cantidad": 1})
    assert resp.status_code == 405  # Method Not Allowed
