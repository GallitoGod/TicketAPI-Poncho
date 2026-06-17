from apps.usuario.serializer import UsuarioSerializer
from apps.usuario.models import Usuario
from rest_framework.test import APIRequestFactory
import pytest
"""
Que se testea aca:
  - El UsuarioSerializer tiene que validar roles (RF-03: solo Soporte puede cambiar el rol).
"""


@pytest.mark.django_db
def test_registro_valido_pasa():
    s = UsuarioSerializer(data={
        "username": "Chocolate_cheap_charly",
        "email": "Chocolate@gmail.com",
        "password": "pass1234",
    })
    assert s.is_valid(), s.errors



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
