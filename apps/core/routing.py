from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/estadisticas/global/', consumers.GraficoGlobalConsumer.as_asgi()),
    path('ws/estadisticas/evento/<uuid:evento_id>', consumers.GraficoConsumer.as_asgi())
]
