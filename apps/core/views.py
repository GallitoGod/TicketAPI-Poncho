from rest_framework import viewsets, permissions
from .models import Evento, SectorEntrada, Ticket
from apps.core.serializer import EventoSerializer, SectorEntradaSerializer, TicketSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]   # Cualquiera puede ver los eventos, pero solo los logueados pueden crear/editar

class SectorEntradaViewSet(viewsets.ModelViewSet):
    queryset = SectorEntrada.objects.all()
    serializer_class = SectorEntradaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]     # Igual que eventos

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]     # Solo los usuarios con token válido pueden entrar acá

    # Esto es para que se asigne el ticket solo al usuario del token
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)