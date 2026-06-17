"""
conftest.py en la raiz del proyecto: pytest lo levanta automaticamente y las
fixtures de aca quedan disponibles en TODOS los archivos de test, sin importar.

Una fixture es simplemente "un dato de arena ya armado" que pido por nombre
como parametro de la funcion de test. Centralizar los usuarios, el evento y el
sector aca evita repetir el mismo setup en cada test.
"""
from decimal import Decimal
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.usuario.models import Usuario
from apps.core.models import Evento, SectorEntrada
from apps.core.engine import MotorDinamico


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def comprador(db):
    return Usuario.objects.create_user(
        username="comprador1", 
        email="comprador@test.com",
        password="pass1234", 
        rol="comprador",
    )


@pytest.fixture
def productor(db):
    return Usuario.objects.create_user(
        username="productor1", 
        email="productor@test.com",
        password="pass1234", 
        rol="productor",
    )


@pytest.fixture
def soporte(db):
    return Usuario.objects.create_user(
        username="soporte1", 
        email="soporte@test.com",
        password="pass1234", 
        rol="soporte",
    )


@pytest.fixture
def evento(db):
    """Evento valido: preventa hoy funcion dentro de 30 dias."""
    hoy = timezone.localdate()
    return Evento.objects.create(
        nombre="Fiesta Nacional del Poncho",
        descripcion="Evento de prueba",
        artista_principal="Soledad Pastorutti",
        bkp_reproducciones=700_111_900,
        preventa=hoy,
        fecha=hoy + timedelta(days=30),
        lugar="Catamarca",
    )


@pytest.fixture
def sector(db, evento):
    """Sector 'Campo' con 100 lugares sin ventas todavia."""
    return SectorEntrada.objects.create(
        evento=evento,
        nombre_sector="Campo",
        capacidad_maxima=100,
        entradas_vendidas=0,
        precio_base_ars=Decimal("10000.00"),
    )


@pytest.fixture
def motor():
    return MotorDinamico(ruta="micro_universo_artistas.csv")
