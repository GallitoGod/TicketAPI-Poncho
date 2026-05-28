from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Usuario(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLES = (
        ('comprador', 'Comprador'),
        ('productor', 'Productor'),
        ('soporte', 'Soporte'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='comprador')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"