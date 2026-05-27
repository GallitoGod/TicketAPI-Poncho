from django.db import models
from django.conf import settings
from apps.usuario.models import Usuario
import uuid

class Evento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    artista_principal = models.CharField(max_length=150)
    spotify_art_id = models.CharField(max_length=100)
    bkp_spotify_popularity = models.IntegerField(default=0)
    fecha = models.DateField(default=None)
    lugar = models.CharField(max_length=150)

    def __str__(self):
        return f"Evento {self.nombre} fecha: {self.fecha}"


class SectorEntrada(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='sectores')
    nombre_sector = models.CharField(max_length=100)
    capacidad_maxima = models.IntegerField()
    entradas_vendidas = models.IntegerField(default=0)
    precio_base_ars = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Sector {self.nombre_sector}"


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tickets')
    sector_entrada = models.ForeignKey(SectorEntrada, on_delete=models.CASCADE, default= None,  related_name= 'tickets')
    cantidad = models.IntegerField()
    precio_final_ars = models.DecimalField(max_digits=12, decimal_places=2)
    bkp_precio_USD = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.usuario}"
