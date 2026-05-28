from rest_framework import viewsets, permissions, filters
from .models import Evento, SectorEntrada, Ticket
from apps.core.serializer import EventoSerializer, SectorEntradaSerializer, TicketSerializer
from apps.core.permissions import EsProductorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EventoFilter, SectorEntradaFilter, TicketFilter

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [EsProductorOrReadOnly] 
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'artista_principal', 'descripcion']
    ordering_fields = ['fecha', 'nombre']
    filterset_class = EventoFilter


class SectorEntradaViewSet(viewsets.ModelViewSet):
    queryset = SectorEntrada.objects.all()
    serializer_class = SectorEntradaSerializer
    permission_classes = [EsProductorOrReadOnly]  
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['precio_base_ars']
    filterset_class = SectorEntradaFilter

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]     # Solo los usuarios con token válido pueden entrar acá
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['fecha_transaccion', 'precio_final_ars']
    filterset_class = TicketFilter

    # Esto es para que se asigne el ticket solo al usuario del token
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

