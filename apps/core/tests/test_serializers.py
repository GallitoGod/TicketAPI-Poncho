from apps.core.serializer import EventoSerializer, SectorEntradaSerializer, TicketSerializer
from rest_framework.test import APIRequestFactory
from django.utils import timezone
from datetime import timedelta
import pytest
"""
Que se testea aca:
  - Los serializers tienen la logica de los requerimientos no funcionales y
    algunos funcionales (RF-01, RF-02, RNF-01, RNF-02).
  - Para cada validacion se prueba el caso que debe fallar y el que debe pasar.

  Al final si tuve que aprender a hacer requests falsas con APIRequestFactory :(
"""


def test_evento_fecha_pasada_es_invalida():
    ayer = timezone.localdate() - timedelta(days=1)
    s = EventoSerializer(data={
        "nombre": "X", 
        "descripcion": "d", 
        "artista_principal": "Ilia Topuria",
        "preventa": timezone.localdate(), 
        "fecha": ayer,
        "lugar": "En la casa del Toto"
    })
    assert not s.is_valid()
    assert "fecha" in s.errors


def test_evento_fecha_futura_es_valida():
    mañana = timezone.localdate() + timedelta(days=10)
    s = EventoSerializer(data={
        "nombre": "X", 
        "descripcion": "d", 
        "artista_principal": "Khabib Habdullmanapovich Nurgomagomedob",
        "preventa": timezone.localdate(), 
        "fecha": mañana, 
        "lugar": "Conter Strike 2",
    })
    assert s.is_valid()


def test_evento_artista_vacio_es_invalido():
    mañana = timezone.localdate() + timedelta(days=10)
    s = EventoSerializer(data={
        "nombre": "X", 
        "descripcion": "d", 
        "artista_principal": "",
        "preventa": timezone.localdate(), 
        "fecha": mañana, 
        "lugar": "White House",
    })
    assert not s.is_valid()
    assert "artista_principal" in s.errors


@pytest.mark.django_db
def test_sector_precio_cero_o_negativo_es_invalido(evento):
    s = SectorEntradaSerializer(data={
        "evento": evento.uuid, 
        "nombre_sector": "Campo",
        "capacidad_maxima": 50, 
        "precio_base_ars": 0.0,
    })
    assert not s.is_valid()
    assert "precio_base_ars" in s.errors


@pytest.mark.django_db
def test_sector_precio_positivo_es_valido(evento):
    s = SectorEntradaSerializer(data={
        "evento": evento.uuid, 
        "nombre_sector": "Campo",
        "capacidad_maxima": 50, 
        "precio_base_ars": 15000.0,
    })
    assert s.is_valid()


@pytest.mark.django_db
def test_ticket_cantidad_cero_es_invalida(sector):
    s = TicketSerializer(data={"sector_entrada": sector.uuid, "cantidad": 0})
    assert not s.is_valid()
    assert "cantidad" in s.errors


@pytest.mark.django_db
def test_ticket_mas_de_cuatro_por_transaccion_es_invalida(sector):
    # validate_cantidad: tope de 4 por compra.
    s = TicketSerializer(data={"sector_entrada": sector.uuid, "cantidad": 5})
    assert not s.is_valid()
    assert "cantidad" in s.errors


@pytest.mark.django_db
def test_ticket_sin_asientos_disponibles_es_invalido(evento, comprador):
    # RNF-01: no se puede comprar mas que la capacidad libre del sector.
    from apps.core.models import SectorEntrada
    chico = SectorEntrada.objects.create(
        evento=evento, 
        nombre_sector="VIP", 
        capacidad_maxima=2,
        entradas_vendidas=0, 
        precio_base_ars=10000.0,
    )
    factory = APIRequestFactory()
    request_falso = factory.post('/otro/coso/')
    request_falso.user = comprador
    s = TicketSerializer(
        data= {
            "sector_entrada": chico.uuid, 
            "cantidad": 3
        },
        context= {
            'request': request_falso
        }
    )
    assert not s.is_valid()  # 3 > 2 disponibles
    assert "cantidad" in s.errors


@pytest.mark.django_db
def test_ticket_compra_valida_pasa(sector, comprador):
    factory = APIRequestFactory()
    request_falso = factory.post('/coso/')
    request_falso.user = comprador
    s = TicketSerializer(
        data= {
            "sector_entrada": sector.uuid, 
            "cantidad": 2
        },
        context= {
            'request': request_falso
        }
    )
    assert s.is_valid()


@pytest.mark.django_db
def test_ticket_limite_por_usuario(sector, comprador):
    from apps.core.models import Ticket
    # El usuario ya compro 4 entradas
    Ticket.objects.create(
        usuario=comprador, 
        sector_entrada=sector, 
        cantidad=4,
        precio_final_ars=1.0, 
        bkp_precio_USD=1.0,
    )
    factory = APIRequestFactory()
    request_falso = factory.post('/algo/')
    request_falso.user = comprador
    s = TicketSerializer(
        data= {
            "sector_entrada": sector.uuid, 
            "cantidad": 1
        },
        context= {
            'request': request_falso
        }
    )
    assert s.is_valid() == False
