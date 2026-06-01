from django.contrib import admin
from .models import Evento, SectorEntrada, Ticket

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'artista_principal', 'fecha', 'lugar', 'bkp_reproducciones')
    search_fields = ('nombre', 'artista_principal', 'lugar')
    list_filter = ('fecha', 'lugar')
    readonly_fields = ('uuid', 'bkp_reproducciones')


@admin.register(SectorEntrada)
class SectorEntradaAdmin(admin.ModelAdmin):
    list_display = ('nombre_sector', 'evento', 'capacidad_maxima', 'entradas_vendidas', 'precio_base_ars')
    search_fields = ('nombre_sector', 'evento__nombre')
    list_filter = ('evento',)
    readonly_fields = ('uuid', 'entradas_vendidas')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'usuario', 'sector_entrada', 'cantidad', 'precio_final_ars', 'fecha_transaccion')
    search_fields = ('usuario__username', 'usuario__email', 'sector_entrada__nombre_sector')
    list_filter = ('fecha_transaccion', 'sector_entrada__evento')
    readonly_fields = ('uuid', 'precio_final_ars', 'bkp_precio_USD', 'fecha_transaccion', 'cantidad', 'usuario', 'sector_entrada')
