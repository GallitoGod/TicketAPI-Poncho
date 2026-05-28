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
            'id', 'nombre', 'descripcion', 
            'artista_principal', 'spotify_art_id',
            'bkp_spotify_popularity', 'fecha', 'lugar',
        ]
        read_only_fields = ['id', 'spotify_art_id', 'bkp_spotify_popularity']

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
            'id', 'evento', 'nombre_sector',
            'capacidad_maxima', 'entradas_vendidas',
            'precio_base_ars',
        ]
        read_only_fields = ['id', 'entradas_vendidas']

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
        model = SectorEntrada
        fields = [
            'id', 'usuario', 'sector_entrada',
            'cantidad', 'precio_final_ars',
            'bkp_precio_USD', 'fecha_transaccion',
        ]
        read_only_fields = ['id']

    def validate_cantidad(self, value):
        """  Control de sobreventa RNF-02:
            El objetivo de este validator es asegurar que no se pueda comprar mas de 4
        entradas en una misma transaccion o comprar valores menores iguales a 0.
        """
        if value <= 0:
            raise serializers.ValidationError("La cantidad de entradas debe ser mayor a cero.")
        if value > 4:
            raise serializers.ValidationError("No es posible comprar mas de 4 entradas por ticket.") # 
        return value
    
    def validate(self, data):
        sector = data['sector_entrada'] 
        cantidad = data['cantidad'] 
        """   Comprobar datos cruzados entre modelos RNF-01:
            El objetivo de este validator es es comprobar si es posible hacer la transaccion con
        respecto a la cantidad de 'asientos' que quedan disponibles en el sector que se quiere
        comprar la/s entrada/s.
        """
        asientos_disponibles = sector.capacidad_maxima - sector.entradas_vendidas 
        if cantidad > asientos_disponibles:
            raise serializers.ValidationError({
                "cantidad": f"No hay suficiente espacio. Asientos disponibles: {asientos_disponibles}."
            })
        return data