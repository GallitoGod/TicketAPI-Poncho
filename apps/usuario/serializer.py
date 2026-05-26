from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'rol']
        read_only_fields = ['id', 'rol']
        extra_kwargs = { # Esto es para en caso de una peticion GET, no leer la contraseña
            'password': {'write_only': True}
        }