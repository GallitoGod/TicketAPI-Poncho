from rest_framework import permissions

# Estos permisos los personalizamos para solo lectura para cualquier usuario (SAFE_METHODS)
# y escritura solo para los usuarios con el rol 'productor' o 'soporte'
class EsProductor_SoporteOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Si es una petición segura
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Para métodos que modifican los datos como POST, PATCH, DELETE:
        # El usuario debe estar autenticado y debe ser 'productor' o 'soporte'
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.rol == 'productor' or request.user.rol == 'soporte')
        )