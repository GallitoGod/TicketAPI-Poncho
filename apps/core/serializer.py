from rest_framework import serializers
from .models import Evento, SectorEntrada, Ticket
from django.utils import timezone

class EventoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Evento
        fields = [
            'uuid', 'nombre', 'descripcion', 
            'artista_principal', 'spotify_art_id',
            'bkp_spotify_popularity', 'fecha', 'lugar',
        ]
        read_only_fields = ['uuid', 'spotify_art_id', 'bkp_spotify_popularity']


class SectorEntradaSerializer(serializers.ModelSerializer):

    class Meta: 
        model = SectorEntrada
        fields = [
            'uuid', 'evento', 'nombre_sector',
            'capacidad_maxima', 'entradas_vendidas',
            'precio_base_ars',
        ]
        read_only_fields = ['uuid', 'entradas_vendidas']

class TicketSerializer (serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            'uuid','usuario', 'sector_entrada',
            'cantidad', 'precio_final_ars',
            'bkp_precio_USD', 'fecha_transaccion',
        ]
        read_only_fields = [
            'uuid', 'bkp_precio_USD', 'fecha_transaccion', 
            'cantidad', 'precio_final_ars'
        ]