from apps.core.permissions import EsProductor_SoporteOrReadOnly
from types import SimpleNamespace
import pytest

"""
Que se testea aca:
  - Restringir permisos para los no picantes: todos pueden leer pero escribir solo los
    picantes.

Dato importante: en estos tests necesito usar APIRequestFactory pero como no se como funciona
directamente voy a buscar los errores forbiden. (Solucion criolla)
"""


# @pytest.mark.django_db
# def test_get_permitido_para_anonimo(api_client):
#     request = api_client.get("/index/evento/")
#     request.user = _user(autenticado=False)
#     assert permiso.has_permission(request, view=None) is True
# Esto no funciona pero si puedo ver los codigos de error y buscar los forbiden


#   La lectura esta permitida para todos
@pytest.mark.django_db
def test_get_permitido_para_anonimo(api_client):
    resp = api_client.get('/index/evento/')
    assert resp.status_code == 200



#   La escritura depende del rol
@pytest.mark.django_db
def test_post_anonimo_denegado(api_client):
    resp = api_client.post("/index/evento/", {
        "nombre": "Recital", 
        "descripcion": "d", 
        "artista_principal": "Luck Ra",
        "preventa": "2030-01-01", 
        "fecha": "2030-02-01", 
        "lugar": "Catamarca",
    })
    assert resp.status_code == 403

@pytest.mark.django_db
def test_post_comprador_denegado(api_client, comprador):
    api_client.force_authenticate(comprador)
    resp = api_client.post('/index/evento/', {
        "nombre": "Recital", 
        "descripcion": "d", 
        "artista_principal": "Luck Ra",
        "preventa": "2030-01-01", 
        "fecha": "2030-02-01", 
        "lugar": "Catamarca",
    })
    assert resp.status_code == 403

@pytest.mark.django_db
def test_post_productor_permitido(api_client, productor):
    api_client.force_authenticate(productor)
    resp = api_client.post('/index/evento/', {
        "nombre": "Recital", 
        "descripcion": "d", 
        "artista_principal": "Luck Ra",
        "preventa": "2030-01-01", 
        "fecha": "2030-02-01", 
        "lugar": "Catamarca",
    })
    assert resp.status_code == 201


@pytest.mark.django_db
def test_delete_soporte_permitido(api_client, soporte, evento):
    api_client.force_authenticate(soporte)
    resp = api_client.delete(f'/index/evento/{evento.uuid}/')
    assert resp.status_code == 204