from apps.usuario.serializer import UsuarioSerializer
from apps.usuario.models import Usuario
from rest_framework.test import APIRequestFactory
import pytest
"""
Que se testea aca:
  - El UsuarioSerializer tiene la logica de registro (email obligatorio, email
    unico) y la validacion de roles (RF-03: solo Soporte puede cambiar el rol).
  - Para cada validacion se prueba el caso que falla y el que pasa.

  Igual que en los serializers de core, cuando hace falta el request lo armo a
  mano con APIRequestFactory.
"""


@pytest.mark.django_db
def test_email_obligatorio_es_invalido():
    s = UsuarioSerializer(data={
        "username": "nuevo",
        "password": "pass1234",
    })
    assert not s.is_valid()
    assert "email" in s.errors


@pytest.mark.django_db
def test_registro_valido_pasa():
    s = UsuarioSerializer(data={
        "username": "nuevo",
        "email": "nuevo@test.com",
        "password": "pass1234",
    })
    assert s.is_valid(), s.errors


@pytest.mark.django_db
def test_email_duplicado_es_invalido(comprador):
    # comprador ya existe con comprador@test.com
    s = UsuarioSerializer(data={
        "username": "otro",
        "email": "comprador@test.com",
        "password": "pass1234",
    })
    assert not s.is_valid()
    assert "email" in s.errors


@pytest.mark.django_db
def test_comprador_no_puede_cambiar_rol(comprador):
    # RF-03: un comprador no puede subirse a productor.
    factory = APIRequestFactory()
    request_falso = factory.patch("/algo/")
    request_falso.user = comprador
    s = UsuarioSerializer(
        instance=comprador,
        data={"rol": "productor"},
        partial=True,
        context={"request": request_falso},
    )
    assert not s.is_valid()
    assert "rol" in s.errors
