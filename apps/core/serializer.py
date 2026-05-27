from rest_framework import serializers
from .models import Evento, SectorEntrada, Ticket
from django.utils import timezone

class EventoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Evento
        fields = [
            'id', 'nombre', 'descripcion', 
            'artista_principal', 'spotify_art_id',
            'bkp_spotify_popularity', 'fecha', 'lugar',
        ]
        read_only_fields = ['id', 'spotify_art_id', 'bkp_spotify_popularity']


class SectorEntradaSerializer(serializers.ModelSerializer):

    class Meta: 
        model = SectorEntrada
        fields = [
            'id', 'evento', 'nombre_sector',
            'capacidad_maxima', 'entradas_vendidas',
            'precio_base_ars',
        ]
        read_only_fields = ['id', 'entradas_vendidas']

class TicketSerializer (serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            'id','usuario', 'sector_entrada',
            'cantidad', 'precio_final_ars',
            'bkp_precio_USD', 'fecha_transaccion',
        ]
        read_only_fields = [
            'id', 'bkp_precio_USD', 'fecha_transaccion', 
            'cantidad', 'precio_final_ars'
        ]