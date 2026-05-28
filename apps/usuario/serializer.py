from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    # email obligatorio
    email = serializers.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ['uuid', 'username', 'email', 'password', 'rol']
        read_only_fields = ['uuid']
        extra_kwargs = { # Esto es para en caso de una peticion GET, no leer la contraseña
            'password': {'write_only': True}
        }

    def validate_rol(self, value):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("No se pudo verificar la identidad para validar el rol.")

        # Validacion para la modificacion de roles RF-03
        
        if self.instance and self.instance.rol != value:
            # Solo los perfiles de Soporte pueden alterar el campo de rol
            rol_solicitante = getattr(request.user, 'rol', 'Comprador')
            if rol_solicitante not in ['Soporte']:
                raise serializers.ValidationError("No tienes permisos para modificar roles.")
        return value
    

    def validate_email(self, value):
        # Comprobando que el email no existe:
        if not self.instance and Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value
    
   

    