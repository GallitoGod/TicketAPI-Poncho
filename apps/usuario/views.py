from rest_framework import viewsets, permissions
from .models import Usuario
from apps.usuario.serializer import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    lookup_field = 'uuid'
