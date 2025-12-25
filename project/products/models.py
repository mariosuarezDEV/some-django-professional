from django.db import models
from core.models import AuditModel
# Create your models here.


class ProductModel(AuditModel):
    imagen = models.ImageField(upload_to='products/', null=True, blank=True)
    nombre = models.CharField(max_length=100, null=False, blank=False,
                              verbose_name='Nombre del Producto', help_text='Ingrese el nombre del producto')
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripción del Producto',
                                   help_text='Ingrese la descripción del producto')
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False,
                                 verbose_name='Precio del Producto', help_text='Ingrese el precio del producto')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
