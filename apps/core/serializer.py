from rest_framework import serializers
from .models import Evento, SectorEntrada, Ticket
from django.utils import timezone

class EventoSerializer(serializers.ModelSerializer):
    """
        Este serializador va a ser utilizado solo por los perfiles productor y soporte
    para la modificacion de capacidades del predio.
    """
    class Meta:
        model = Evento
        fields = [
            'uuid', 'nombre', 'descripcion', 
            'artista_principal', 'spotify_art_id',
            'bkp_spotify_popularity', 'fecha', 'lugar',
        ]
        read_only_fields = ['uuid', 'spotify_art_id', 'bkp_spotify_popularity']

    def validate_fecha_hora(self, value):
        # Control de tiempo para la cartelera RF-01
        if value < timezone.now():
            raise serializers.ValidationError("La fecha y hora del evento debe ser una fecha futura.")
        return value


class SectorEntradaSerializer(serializers.ModelSerializer):
    """
        Este serializador va a ser utilizado solo por los perfiles productor y soporte
    para la modificacion de capacidades del predio.
    """
    class Meta: 
        model = SectorEntrada
        fields = [
            'uuid', 'evento', 'nombre_sector',
            'capacidad_maxima', 'entradas_vendidas',
            'precio_base_ars',
        ]
        read_only_fields = ['uuid', 'entradas_vendidas']

    def validate_precio_base_ars(self, value):
        # Control de valores RF-02
        if value <= 0:
            raise serializers.ValidationError("El precio base en pesos debe ser mayor a cero.")
        return value
    
    def validate_entradas_vendidas(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad de entradas vendidas no puede ser negativa.")
        return value
    

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
