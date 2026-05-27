from rest_framework import viewsets, permissions
from .models import Evento, SectorEntrada, Ticket
from apps.core.serializer import EventoSerializer, SectorEntradaSerializer, TicketSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SectorEntradaViewSet(viewsets.ModelViewSet):
    queryset = SectorEntrada.objects.all()
    serializer_class = SectorEntradaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]