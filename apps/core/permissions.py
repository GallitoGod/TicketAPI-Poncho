from rest_framework import permissions

class EsProductorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Si es una petición segura
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Si es para modificar (POST, PUT, etc.), verificamos el rol
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'productor')