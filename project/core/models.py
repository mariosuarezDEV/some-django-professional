from django.db import models
# Personalizar el modelo de usuario
from django.contrib.auth.models import AbstractUser


class UserModel(AbstractUser):
    # Campos adicionales para el modelo de usuario
    pass


class AuditModel(models.Model):
    # Fecha
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Usuario
    created_by = models.ForeignKey(
        UserModel,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name='created_%(class)s_set'
    )
    updated_by = models.ForeignKey(
        UserModel,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name='updated_%(class)s_set'
    )
    active = models.BooleanField(
        default=True, help_text="Indica si el registro está activo.", db_index=True, verbose_name="Activo")

    class Meta:
        abstract = True
