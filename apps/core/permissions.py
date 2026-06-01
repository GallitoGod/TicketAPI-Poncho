from rest_framework import permissions

class EsProductor_SoporteOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Si es una petición segura
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.rol == 'productor' or request.user.rol == 'soporte')
        )