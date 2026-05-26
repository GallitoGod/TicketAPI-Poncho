from django.db import models
from django.conf import settings

class Evento(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    artista_principal = models.CharField(max_length=150)
    spotify_art_id = models.CharField(max_length=100)
    bkp_spotify_popularity = models.IntegerField(default=0)
    fecha_hora = models.DateTimeField()
    lugar = models.CharField(max_length=150)


class SectorEntrada(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='sectores')
    nombre_sector = models.CharField(max_length=100)
    capacidad_maxima = models.IntegerField()
    entradas_vendidas = models.IntegerField(default=0)
    precio_base_ars = models.DecimalField(max_digits=12, decimal_places=2)


class Ticket(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    sector_entrada = models.ForeignKey('SectorEntrada', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_final_ars = models.DecimalField(max_digits=12, decimal_places=2)
    bkp_precio_USD = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)

