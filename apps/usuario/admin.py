from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class CustomUserAdmin(UserAdmin):
    model = Usuario
    # Para ver al usuario en el panel
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol', {'fields': ('rol',)}),
    )
    list_display = ['username', 'email', 'rol', 'is_staff']

admin.site.register(Usuario, CustomUserAdmin)

