from rest_framework import serializers
from .models import Evento, SectorEntrada, Ticket
from django.utils import timezone
from django.db.models import Sum

class EventoSerializer(serializers.ModelSerializer):
    """
        Este serializador va a ser utilizado solo por los perfiles productor y soporte
    para la modificacion de capacidades del predio.
    """
    class Meta:
        model = Evento
        fields = [
            'uuid', 'nombre', 'descripcion', 
            'artista_principal', 'bkp_reproducciones',
            'preventa', 'fecha', 'lugar'
        ]
        read_only_fields = ['uuid', 'bkp_reproducciones']

    def validate_fecha(self, value):
        # Control de tiempo para la cartelera RF-01
        if value < timezone.now().date():
            raise serializers.ValidationError("La fecha del evento debe ser una fecha futura.")
        return value
    
    def validate_artista_principal(self, value):
        if not value: 
            raise serializers.ValidationError("No se puede cargar un evento sin artista principal")
        return value


class SectorEntradaSerializer(serializers.ModelSerializer):
    """
        Este serializador va a ser utilizado solo por los perfiles productor y soporte
    para la modificacion de capacidades del predio.
    """
    evento = EventoSerializer()
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
            'uuid', 'bkp_precio_USD', 'fecha_transaccion' , 'precio_final_ars', 'usuario']
        
    def validate(self, data):
        """  Control de sobreventa RNF-02:
            No permite mas compras de tickest una vez alcanzada la cantidad maxima de entradas.
        """
        usuario = data.get('usuario')
        cantidad = data.get('cantidad')
        cant_por_ticket = Ticket.objects.filter(usuario= usuario).aggregate(
            entradas_ya_compradas= Sum('cantidad')
        )
        historial_de_compras = cant_por_ticket['entradas_ya_compradas'] or 0

        if historial_de_compras + cantidad > 4:
            raise serializers.ValidationError("Limite de entradas por usuario excedido")
        return data
    
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
        sector = data.get('sector_entrada')
        cantidad = data.get('cantidad') 
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