from rest_framework import viewsets, permissions
from .models import Usuario
from apps.usuario.serializer import UsuarioSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(summary="Listar Usuario", description="Obtiene todos los Usuarios.", tags=['Usuarios']),
    create=extend_schema(summary="Crear Usuario", description="Registra un nuevo Usuario.", tags=['Usuarios']),
    retrieve=extend_schema(summary="Ver detalle del Usuario", tags=['Usuarios']),
    update=extend_schema(summary="Actualizar Usuario", description="Reemplaza completamente un Usuario.", tags=['Usuarios']),
    partial_update=extend_schema(summary="Actualizar parcialmente Usuario", description="Modifica campos específicos del Usuario.", tags=['Usuarios']),
    destroy=extend_schema(summary="Eliminar Usuario", description="Elimina un Usuario por UUID.", tags=['Usuarios'])
)
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    lookup_field = 'uuid'
