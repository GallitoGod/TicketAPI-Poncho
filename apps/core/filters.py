import django_filters
from .models import Evento, SectorEntrada, Ticket

class EventoFilter(django_filters.FilterSet):

    fecha_desde = django_filters.DateFilter(field_name="fecha", lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name="fecha", lookup_expr='lte')
    
    
    lugar = django_filters.CharFilter(field_name="lugar", lookup_expr='icontains') # icontains hace la búsqueda sin importar mayúsculas

    class Meta:
        model = Evento
        fields = ['fecha', 'lugar'] 

class SectorEntradaFilter(django_filters.FilterSet):
    class Meta:
        model = SectorEntrada
        fields = ['evento']

class TicketFilter(django_filters.FilterSet):
    class Meta:
        model = Ticket
        fields = ['sector_entrada']