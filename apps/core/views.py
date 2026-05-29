from rest_framework import viewsets, permissions, filters
from .models import Evento, SectorEntrada, Ticket
from apps.core.serializer import EventoSerializer, SectorEntradaSerializer, TicketSerializer
from apps.core.permissions import EsProductorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EventoFilter, SectorEntradaFilter, TicketFilter
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(summary="Listar Eventos", description="Obtiene todos los eventos con los filtros y la paginación ya aplicada.", tags=['Eventos']),
    create=extend_schema(summary="Crear Evento", description="Registra un nuevo evento", tags=['Eventos']),
    retrieve=extend_schema(summary="Ver detalle de Evento", tags=['Eventos']),
    update=extend_schema(summary="Actualizar Evento", description="Reemplaza completamente un evento.", tags=['Eventos']),
    partial_update=extend_schema(summary="Actualizar parcialmente Evento", description="Modifica campos específicos del evento.", tags=['Eventos']),
    destroy=extend_schema(summary="Eliminar Evento", description="Elimina un evento por UUID.", tags=['Eventos'])
)
class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [EsProductorOrReadOnly] 
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'artista_principal', 'descripcion']
    ordering_fields = ['fecha', 'nombre']
    filterset_class = EventoFilter

@extend_schema_view(
    list=extend_schema(summary="Listar Sectores", description="Obtiene todos los sectores de los eventos.", tags=['Sectores']),
    create=extend_schema(summary="Crear Sector", description="Registra un nuevo Sector", tags=['Sectores']),
    retrieve=extend_schema(summary="Ver detalle del Sector", tags=['Sectores']),
    update=extend_schema(summary="Actualizar Sector", description="Reemplaza completamente un sector.", tags=['Sectores']),
    partial_update=extend_schema(summary="Actualizar parcialmente Sector", description="Modifica campos específicos del sector.", tags=['Sectores']),
    destroy=extend_schema(summary="Eliminar Sector", description="Elimina un sector por UUID.", tags=['Sectores'])
)
class SectorEntradaViewSet(viewsets.ModelViewSet):
    queryset = SectorEntrada.objects.all()
    serializer_class = SectorEntradaSerializer
    permission_classes = [EsProductorOrReadOnly]  
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['precio_base_ars']
    filterset_class = SectorEntradaFilter


@extend_schema_view(
    list=extend_schema(summary="Listar Tickets", description="Obtiene todos los tickets.", tags=['Tickets']),
    create=extend_schema(summary="Crear Ticket", description="Registra un nuevo Ticket", tags=['Tickets']),
    retrieve=extend_schema(summary="Ver detalle del Ticket", tags=['Tickets']),
    update=extend_schema(summary="Actualizar Ticket", description="Reemplaza completamente un ticket.", tags=['Tickets']),
    partial_update=extend_schema(summary="Actualizar parcialmente Ticket", description="Modifica campos específicos del ticket.", tags=['Tickets']),
    destroy=extend_schema(summary="Eliminar Ticket", description="Elimina un ticket por UUID.", tags=['Tickets'])
)
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['fecha_transaccion', 'precio_final_ars']
    filterset_class = TicketFilter

    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

