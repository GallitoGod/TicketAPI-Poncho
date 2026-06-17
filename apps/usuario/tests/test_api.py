import pytest
from apps.usuario.models import Usuario
"""
Que se testea aca:
  - El flujo de alta de usuarios por el endpoint (POST /index/usuario/).
  - El login JWT contra /api/token/, que es lo que el resto de los tests de core
    no prueban (alla uso force_authenticate). Aca chequeo que el token salga.
"""


@pytest.mark.django_db
def test_crear_usuario_ok(api_client, soporte):
    api_client.force_authenticate(user=soporte)
    resp = api_client.post("/index/usuario/", {
        "username": "Chocolate_cheap_charly",
        "email": "ChocoCharly@gmail.com",
        "password": "pass1234",
    })
    assert resp.status_code == 201, resp.data
    # por defecto el rol es comprador
    assert resp.data["rol"] == "comprador"
    assert Usuario.objects.filter(username="Chocolate_cheap_charly").exists()


@pytest.mark.django_db
def test_ver_usuario_no_devuelve_password(api_client, comprador):
    api_client.force_authenticate(user=comprador)
    resp = api_client.get(f"/index/usuario/{comprador.uuid}/")
    assert resp.status_code == 200
    assert "password" not in resp.data


@pytest.mark.django_db
def test_login_jwt_devuelve_tokens(api_client, comprador):
    # el fixture crea el usuario con password "pass1234"
    resp = api_client.post("/api/token/", {
        "username": "comprador1",
        "password": "pass1234",
    })
    assert resp.status_code == 200, resp.data
    assert "access" in resp.data


@pytest.mark.django_db
def test_login_jwt_credenciales_invalidas(api_client, comprador):
    resp = api_client.post("/api/token/", {
        "username": "comprador1",
        "password": "contraseñaMal",
    })
    assert resp.status_code == 401
