from rest_framework import routers
from apps.core.views import EventoViewSet, SectorEntradaViewSet, TicketViewSet
from apps.usuario.views import UsuarioViewSet
from django.urls import path, include

router = routers.DefaultRouter()
# Con este objeto basicamente tengo un mapeo dinamico de todos los endpoints de las viewSet
"""
    Y pasa algo importante con DefaultRouter que no tiene SimpleRouter:

    DefaultRouter crea una vista raiz '/' donde hay un indice que permite ver los endpoints disponibles.
    SimpleRouter al buscar esa vista raiz '/' daria error 404.
"""

router.register(prefix= 'evento', viewset= EventoViewSet)
# "prefix" se refiere al nombre con el que buscar, en la url, la API CRUD del viewSet que le pasamos por "viewset"
router.register(prefix= 'sectorEntrada', viewset= SectorEntradaViewSet)
router.register(prefix= 'ticket', viewset= TicketViewSet)
router.register(prefix= 'usuario', viewset= UsuarioViewSet)

urlpatterns = router.urls


