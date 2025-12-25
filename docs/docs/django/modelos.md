# Guía Completa de Models.py en Django

Los modelos son el corazón de Django, actuando como la única fuente de verdad sobre tus datos. Esta guía exhaustiva cubre todo lo que puedes hacer con ellos, desde lo básico hasta técnicas avanzadas.

## 1. Definición básica de modelos

```python
from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    en_stock = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
```

## 2. Todos los tipos de campos disponibles

### Campos de texto

```python
# Cadenas cortas
titulo = models.CharField(max_length=200)  # Requerido especificar max_length
codigo = models.SlugField(max_length=50)   # Letras, números, guiones, guiones bajos
nombre_usuario = models.SlugField(max_length=30, allow_unicode=True)  # Permite Unicode

# URLs y correos
sitio_web = models.URLField(max_length=200)  # Valida formato URL
email = models.EmailField(max_length=254)    # Valida formato email

# Texto largo
descripcion = models.TextField()  # Texto ilimitado
html_content = models.TextField(help_text="Contenido HTML de la página")
```

### Campos numéricos

```python
# Enteros
edad = models.IntegerField()  # -2147483648 a 2147483647
cantidad = models.PositiveIntegerField()  # 0 a 2147483647
plazas = models.PositiveSmallIntegerField()  # 0 a 32767
poblacion = models.BigIntegerField()  # -9223372036854775808 a 9223372036854775807

# Decimales
precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precisión exacta
altura = models.FloatField()  # Coma flotante (menos preciso pero más rápido)

# Booleanos
activo = models.BooleanField(default=True)
enviado = models.BooleanField()
```

### Campos de fecha y hora

```python
fecha_nacimiento = models.DateField()
hora_entrega = models.TimeField()
fecha_hora_creacion = models.DateTimeField()
fecha_modificacion = models.DateTimeField(auto_now=True)  # Se actualiza en cada save()
fecha_creacion = models.DateTimeField(auto_now_add=True)  # Solo se establece en create()
duracion = models.DurationField()  # Para almacenar períodos de tiempo
```

### Campos de archivo

```python
# Archivos y imágenes
documento = models.FileField(upload_to='documentos/')
imagen = models.ImageField(upload_to='imagenes/%Y/%m/')  # Requiere Pillow
archivo_pdf = models.FileField(
    upload_to='pdfs/',
    validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
)

# Campos especializados para almacenar ubicaciones de archivos
imagen_portada = models.FilePathField(path='/var/www/images/')
```

### Otros campos

```python
# Campos binarios
datos = models.BinaryField()  # Para almacenar datos binarios brutos

# JSON y otros formatos
configuracion = models.JSONField(default=dict)  # Requiere PostgreSQL o similar

# Campos especiales
uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True)
```

## 3. Opciones comunes para todos los campos

```python
class Producto(models.Model):
    nombre = models.CharField(
        max_length=100,                 # Longitud máxima (obligatorio para CharField)
        verbose_name="Nombre producto", # Nombre legible para humanos
        help_text="Ingrese el nombre del producto", # Texto de ayuda
        null=True,                      # Permite valores NULL en la BD
        blank=True,                     # Permite valores vacíos en formularios
        default="Producto nuevo",       # Valor por defecto
        editable=False,                 # No se muestra en formularios
        unique=True,                    # Valor único en la tabla
        db_index=True,                  # Crea índice en la BD para este campo
        primary_key=False,              # No es clave primaria
        db_column="product_name",       # Nombre de columna específico en la BD
        choices=(                       # Lista predefinida de opciones
            ('S', 'Small'),
            ('M', 'Medium'),
            ('L', 'Large'),
        ),
        validators=[MinLengthValidator(3)], # Lista de validadores
        error_messages={                    # Mensajes de error personalizados
            'null': 'Este campo no puede ser nulo',
            'blank': 'Este campo es obligatorio',
        }
    )
```

## 4. Relaciones entre modelos

### ForeignKey (Relación uno a muchos)

```python
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    # Muchos productos pueden pertenecer a una categoría
    categoria = models.ForeignKey(
        Categoria,                      # Modelo relacionado
        on_delete=models.CASCADE,       # Comportamiento al eliminar: CASCADE, PROTECT, SET_NULL, SET_DEFAULT, DO_NOTHING, SET()
        related_name='productos',       # Nombre para la relación inversa
        related_query_name='producto',  # Nombre para filtros en consultas inversas
        limit_choices_to={'activa': True}, # Limita las opciones disponibles
        db_constraint=True,             # Crea restricción en la BD
        to_field='id',                  # Campo al que se relaciona (por defecto es pk)
        swappable=True,                 # Si se puede intercambiar el modelo relacionado
        db_index=True,                  # Crea índice para este campo
        null=True,                      # Permite nulos
        blank=True                      # Permite vacíos en formularios
    )
    
    # Auto-referencia (un producto puede ser el repuesto de otro)
    repuesto_de = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Referencias a modelos aún no definidos
    creado_por = models.ForeignKey('auth.User', on_delete=models.PROTECT)
```

### ManyToManyField (Relación muchos a muchos)

```python
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    # Un producto puede tener muchas etiquetas y una etiqueta puede estar en muchos productos
    etiquetas = models.ManyToManyField(
        Etiqueta,
        related_name='productos',
        blank=True,
        through='ProductoEtiqueta',     # Modelo para la tabla intermedia personalizada
        through_fields=('producto', 'etiqueta'),  # Campos para la relación en el modelo through
        db_table='producto_etiqueta',   # Nombre de la tabla intermedia en la BD
        symmetrical=False,              # Para relaciones ManyToMany con 'self'
    )
    
    # Auto-referencia (productos compatibles con este producto)
    compatible_con = models.ManyToManyField('self', blank=True, symmetrical=False)

# Tabla intermedia personalizada para añadir campos a la relación
class ProductoEtiqueta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        # Garantiza que no haya duplicados
        unique_together = [['producto', 'etiqueta']]
```

### OneToOneField (Relación uno a uno)

```python
class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

class Perfil(models.Model):
    # Un perfil pertenece a un solo empleado y un empleado tiene un solo perfil
    empleado = models.OneToOneField(
        Empleado,
        on_delete=models.CASCADE,
        primary_key=True,          # Usa el mismo ID que el empleado
        parent_link=True,          # Para herencia multi-tabla
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
```

## 5. Métodos y propiedades personalizados

```python
from django.utils import timezone
import datetime

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    fecha_caducidad = models.DateField(null=True, blank=True)
    
    # Propiedad calculada
    @property
    def margen(self):
        """Calcula el margen de beneficio"""
        if self.costo == 0:
            return 0
        return ((self.precio - self.costo) / self.precio) * 100
    
    # Propiedad con setter
    @property
    def precio_con_iva(self):
        """Precio con IVA incluido"""
        return self.precio * 1.21
        
    @precio_con_iva.setter
    def precio_con_iva(self, valor):
        """Establece el precio sin IVA a partir del precio con IVA"""
        self.precio = valor / 1.21
    
    # Método de instancia
    def esta_disponible(self):
        """Determina si el producto está disponible"""
        if self.stock <= 0:
            return False
        if self.fecha_caducidad and self.fecha_caducidad <= timezone.now().date():
            return False
        return True
    
    # Método con parámetros
    def aplicar_descuento(self, porcentaje):
        """Aplica un descuento al precio del producto"""
        if porcentaje < 0 or porcentaje > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        self.precio = self.precio * (1 - (porcentaje / 100))
        return self.precio
    
    # Método que modifica múltiples campos
    def recibir_stock(self, cantidad, nuevo_costo=None):
        """Añade stock y actualiza el costo si se proporciona"""
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        
        self.stock += cantidad
        
        if nuevo_costo is not None:
            self.costo = nuevo_costo
            
        self.save(update_fields=['stock', 'costo'])
        return self.stock
        
    # Método que interactúa con otras instancias
    def transferir_stock(self, producto_destino, cantidad):
        """Transfiere stock a otro producto"""
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        if cantidad > self.stock:
            raise ValueError("Stock insuficiente")
            
        self.stock -= cantidad
        producto_destino.stock += cantidad
        
        self.save(update_fields=['stock'])
        producto_destino.save(update_fields=['stock'])
    
    # Método que devuelve un valor complejo o QuerySet
    def obtener_productos_similares(self):
        """Encuentra productos con precios similares"""
        min_precio = self.precio * 0.9
        max_precio = self.precio * 1.1
        
        return Producto.objects.filter(
            precio__gte=min_precio,
            precio__lte=max_precio
        ).exclude(id=self.id)
```

## 6. Métodos estáticos y de clase

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Método estático (no accede a la instancia ni a la clase)
    @staticmethod
    def convertir_moneda(precio, tasa_cambio):
        """Convierte un precio a otra moneda usando la tasa de cambio"""
        return precio * tasa_cambio
    
    # Método de clase (accede a la clase pero no a la instancia)
    @classmethod
    def crear_oferta(cls, nombre, precio_original, descuento_porcentaje):
        """Crea un nuevo producto con descuento aplicado"""
        precio_con_descuento = precio_original * (1 - (descuento_porcentaje / 100))
        return cls.objects.create(
            nombre=f"{nombre} (Oferta {descuento_porcentaje}%)",
            precio=precio_con_descuento
        )
    
    # Método de clase que devuelve un QuerySet
    @classmethod
    def obtener_productos_caros(cls):
        """Obtiene productos con precio superior a la media"""
        from django.db.models import Avg
        precio_medio = cls.objects.aggregate(Avg('precio'))['precio__avg']
        return cls.objects.filter(precio__gt=precio_medio)
```

## 7. Sobreescritura de métodos del modelo

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    # Personalizar representación en string
    def __str__(self):
        return f"{self.nombre} ({self.id})"
    
    # Personalizar representación en depuración
    def __repr__(self):
        return f"<Producto: {self.id}, {self.nombre}>"
    
    # Personalizar el comportamiento de guardado
    def save(self, *args, **kwargs):
        # Acciones antes de guardar
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nombre)
            
        # Validaciones personalizadas
        if len(self.nombre) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
            
        # Llamar al método original
        super().save(*args, **kwargs)
        
        # Acciones después de guardar
        self.crear_thumbnail()
    
    # Personalizar el comportamiento de eliminación
    def delete(self, *args, **kwargs):
        # Acciones antes de eliminar
        self.eliminar_archivos_asociados()
        
        # Llamar al método original
        super().delete(*args, **kwargs)
        
        # Acciones después de eliminar (cuidado: la instancia ya no existe en la BD)
        
    # Personalizar el comportamiento de validación
    def clean(self):
        """Validaciones a nivel de modelo (no de campo)"""
        from django.core.exceptions import ValidationError
        
        if self.precio < self.costo:
            raise ValidationError("El precio no puede ser menor que el costo")
            
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError({
                'fecha_inicio': "La fecha de inicio no puede ser posterior a la fecha de fin",
                'fecha_fin': "La fecha de fin no puede ser anterior a la fecha de inicio"
            })
    
    # Personalizar URLs
    def get_absolute_url(self):
        """Devuelve la URL única para este objeto"""
        from django.urls import reverse
        return reverse('producto-detalle', kwargs={'slug': self.slug})
```

## 8. Meta opciones

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        # Nombre y plurales para la interfaz de administración
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        
        # Ordenación por defecto
        ordering = ['-fecha_creacion', 'nombre']
        
        # Índices para optimizar consultas
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['precio', 'categoria']),
            models.Index(fields=['-fecha_creacion'], name='idx_fecha_creacion_desc'),
        ]
        
        # Restricciones de unicidad compuesta
        unique_together = [['sku', 'tienda'], ['slug', 'categoria']]
        
        # Restricciones de unicidad con condiciones (Django 2.2+)
        constraints = [
            models.UniqueConstraint(
                fields=['sku', 'tienda'], 
                name='unique_sku_por_tienda'
            ),
            models.UniqueConstraint(
                fields=['slug'],
                condition=models.Q(activo=True),
                name='unique_slug_activos'
            ),
            models.CheckConstraint(
                check=models.Q(precio__gte=0),
                name='precio_positivo'
            ),
        ]
        
        # Nombrar la tabla en la base de datos
        db_table = 'inventario_producto'
        
        # Otras opciones Meta
        abstract = False              # Si es True, será un modelo abstracto
        app_label = 'inventario'      # Especifica la app a la que pertenece
        db_tablespace = 'idx_tbls'    # Espacio de tabla para índices
        default_permissions = ('add', 'change', 'delete', 'view')
        default_related_name = 'productos'  # Nombre relacional por defecto
        get_latest_by = 'fecha_creacion'    # Campo para latest() y earliest()
        managed = True                # Si Django gestiona esta tabla
        order_with_respect_to = 'categoria'  # Permite ordenar respecto a otro campo
        permissions = [               # Permisos adicionales
            ('puede_publicar', 'Puede publicar productos'),
            ('puede_destacar', 'Puede destacar productos'),
        ]
        proxy = False                 # Si es modelo proxy
        required_db_features = ['supports_json_field']  # Características requeridas de la BD
        select_on_save = False        # Si hacer SELECT antes de guardar
```

## 9. Managers personalizados

```python
class ProductoActivoManager(models.Manager):
    """Manager que solo devuelve productos activos"""
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)
    
    # Método personalizado del manager
    def destacados(self):
        """Devuelve productos activos y destacados"""
        return self.filter(destacado=True)
    
    # Método para crear objetos con valores por defecto
    def crear_producto_destacado(self, nombre, precio, **kwargs):
        return self.create(
            nombre=nombre,
            precio=precio,
            destacado=True,
            **kwargs
        )

class ProductoDesactivoManager(models.Manager):
    """Manager que solo devuelve productos inactivos"""
    def get_queryset(self):
        return super().get_queryset().filter(activo=False)

class ProductoQuerySet(models.QuerySet):
    """QuerySet personalizado con métodos adicionales"""
    
    def destacados(self):
        return self.filter(destacado=True)
    
    def por_precio(self, precio_min, precio_max):
        return self.filter(precio__gte=precio_min, precio__lte=precio_max)
    
    def agotados(self):
        return self.filter(stock=0)
    
    # Métodos que modifiquen datos en masa
    def destacar_todos(self):
        return self.update(destacado=True)
    
    def subir_precio(self, porcentaje):
        from django.db.models import F
        return self.update(precio=F('precio') * (1 + porcentaje/100))

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    
    # Manager por defecto
    objects = models.Manager()
    
    # Managers adicionales
    activos = ProductoActivoManager()
    inactivos = ProductoDesactivoManager()
    
    # Manager personalizado que devuelve QuerySet personalizado
    todo = models.Manager.from_queryset(ProductoQuerySet)()
    
    def __str__(self):
        return self.nombre
```

Ahora podemos usar:

```python
# Usando los diferentes managers
Producto.objects.all()           # Todos los productos
Producto.activos.all()           # Solo productos activos
Producto.inactivos.all()         # Solo productos inactivos
Producto.activos.destacados()    # Productos activos y destacados

# Usando el QuerySet personalizado
Producto.todo.destacados()
Producto.todo.por_precio(10, 100)
Producto.todo.agotados()

# Operaciones en masa
Producto.todo.filter(categoria=5).destacar_todos()
Producto.todo.filter(marca="Sony").subir_precio(5)
```

## 10. Herencia de modelos

### Herencia abstracta

```python
class ModeloBase(models.Model):
    """Modelo abstracto con campos comunes"""
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        abstract = True  # No crea tabla para este modelo
        
    def activar(self):
        self.activo = True
        self.save(update_fields=['activo'])
        
    def desactivar(self):
        self.activo = False
        self.save(update_fields=['activo'])

class Producto(ModeloBase):
    """Hereda todos los campos y métodos de ModeloBase"""
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Puede añadir sus propias Meta opciones
    class Meta(ModeloBase.Meta):
        verbose_name = "Producto"
        ordering = ['-creado']

class Cliente(ModeloBase):
    """También hereda de ModeloBase"""
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
```

### Herencia multi-tabla

```python
class Producto(models.Model):
    """Modelo base para todos los productos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nombre

class Libro(Producto):
    """Crea una tabla separada con un OneToOneField a Producto"""
    autor = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    paginas = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.nombre} de {self.autor}"

class Electronico(Producto):
    """Otra tabla separada con relación a Producto"""
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    garantia_meses = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.marca} {self.modelo}"
```

### Herencia proxy

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=[
        ('normal', 'Normal'),
        ('destacado', 'Destacado'),
        ('oferta', 'Oferta')
    ])
    
    def __str__(self):
        return self.nombre

class ProductoDestacado(Producto):
    """
    Modelo proxy que no crea nueva tabla, sino que
    proporciona una vista diferente del modelo Producto
    """
    objects = models.Manager()  # Manager por defecto
    
    class Meta:
        proxy = True  # Es un modelo proxy
        ordering = ['-precio']  # Ordenación diferente
    
    def destacar(self):
        self.tipo = 'destacado'
        self.save()
    
    @property
    def precio_original(self):
        """Calcula el precio original antes del descuento"""
        return self.precio * 1.2
```

## 11. Señales (Signals)

```python
# En models.py o en signals.py
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import Producto

@receiver(pre_save, sender=Producto)
def producto_pre_save(sender, instance, **kwargs):
    """Se ejecuta antes de guardar un producto"""
    # Podemos modificar la instancia antes de guardarla
    if instance.stock < 0:
        instance.stock = 0
    
    # Calcular campos derivados
    if instance.precio and instance.costo:
        instance.margen = instance.precio - instance.costo

@receiver(post_save, sender=Producto)
def producto_post_save(sender, instance, created, **kwargs):
    """Se ejecuta después de guardar un producto"""
    if created:
        # Solo si es un producto nuevo
        from .tasks import notificar_nuevo_producto
        notificar_nuevo_producto.delay(instance.id)
    else:
        # Si es una actualización
        if 'precio' in kwargs.get('update_fields', []):
            from .tasks import actualizar_precios_relacionados
            actualizar_precios_relacionados.delay(instance.id)

@receiver(pre_delete, sender=Producto)
def producto_pre_delete(sender, instance, **kwargs):
    """Se ejecuta antes de eliminar un producto"""
    # Guardar registro de eliminación
    from .models import RegistroEliminacion
    RegistroEliminacion.objects.create(
        modelo='Producto',
        objeto_id=instance.id,
        nombre=instance.nombre,
        datos=str(instance.__dict__)
    )
    
    # Eliminar archivos asociados
    if instance.imagen:
        import os
        if os.path.isfile(instance.imagen.path):
            os.remove(instance.imagen.path)

@receiver(post_delete, sender=Producto)
def producto_post_delete(sender, instance, **kwargs):
    """Se ejecuta después de eliminar un producto"""
    # Actualizar caché o búsqueda
    from .tasks import actualizar_cache_productos
    actualizar_cache_productos.delay()

# Señales personalizadas
from django.dispatch import Signal

# Definir una señal personalizada
producto_agotado = Signal()  # Puede incluir providing_args=['producto']

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Actualizar stock
        self.producto.stock -= self.cantidad
        self.producto.save(update_fields=['stock'])
        
        # Emitir señal si el producto se agotó
        if self.producto.stock == 0:
            producto_agotado.send(sender=self.__class__, producto=self.producto)

# En otro lugar, escuchar la señal personalizada
@receiver(producto_agotado)
def notificar_producto_agotado(sender, producto, **kwargs):
    from django.core.mail import send_mail
    send_mail(
        f'Producto agotado: {producto.nombre}',
        f'El producto {producto.nombre} se ha agotado.',
        'sistema@ejemplo.com',
        ['almacen@ejemplo.com'],
    )
```

## 12. Campos personalizados

```python
from django.db import models
from django.core.exceptions import ValidationError

def validar_rango(value):
    if value < 0 or value > 100:
        raise ValidationError('El valor debe estar entre 0 y 100')

class RangoEnteroField(models.IntegerField):
    """Campo entero con validación de rango personalizada"""
    
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        # Personaliza el campo de formulario
        defaults = {
            'min_value': self.min_value,
            'max_value': self.max_value,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
    
    def deconstruct(self):
        # Necesario para las migraciones
        name, path, args, kwargs = super().deconstruct()
        if self.min_value is not None:
            kwargs['min_value'] = self.min_value
        if self.max_value is not None:
            kwargs['max_value'] = self.max_value
        return name, path, args, kwargs
    
    def validate(self, value, model_instance):
        # Validación personalizada
        super().validate(value, model_instance)
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f'El valor debe ser mayor o igual a {self.min_value}')
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f'El valor debe ser menor o igual a {self.max_value}')

class ColorField(models.CharField):
    """Campo para almacenar colores en formato hexadecimal"""
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super().__init__(*args, **kwargs)
    
    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        if value and not value.startswith('#'):
            value = f'#{value}'
        return value
        
    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value:
            import re
            if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
                raise ValidationError('Formato de color hexadecimal inválido')

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    calificacion = RangoEnteroField(min_value=1, max_value=5, help_text="Calificación de 1 a 5 estrellas")
    color_principal = ColorField(null=True, blank=True, help_text="Color en formato hexadecimal (#RRGGBB)")
```

## 13. Operaciones avanzadas con QuerySets

```python
from django.db.models import F, Q, Count, Sum, Avg, Min, Max, Case, When, Value, IntegerField, CharField
from django.db.models.functions import ExtractYear, ExtractMonth, Concat

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def consultas_avanzadas(cls):
        # Ejemplos de consultas avanzadas
        
        # F expressions - Operaciones a nivel de base de datos
        cls.objects.update(precio=F('precio') * 1.1)  # Aumenta todos los precios un 10%
        
        # Productos cuyo precio es mayor que el precio base
        productos_caros = cls.objects.filter(precio__gt=F('precio_base'))
        
        # Productos con más ventas que stock
        productos_exitosos = cls.objects.filter(ventas_totales__gt=F('stock'))
        
        # Q expressions - Consultas complejas con OR, AND, NOT
        from django.db.models import Q
        
        # Productos baratos O con stock alto
        productos = cls.objects.filter(
            Q(precio__lt=10) | Q(stock__gt=100)
        )
        
        # Productos caros Y de categoría específica, excluyendo una marca
        productos = cls.objects.filter(
            Q(precio__gt=50) & 
            Q(categoria__nombre='Electrónica') &
            ~Q(marca='Marca Genérica')
        )
        
        # Funciones de agregación
        from django.db.models import Avg, Count, Min, Max, Sum
        
        # Estadísticas generales
        stats = cls.objects.aggregate(
            total_productos=Count('id'),
            precio_promedio=Avg('precio'),
            precio_minimo=Min('precio'),
            precio_maximo=Max('precio'),
            valor_inventario=Sum(F('precio') * F('stock'))
        )
        
        # Anotaciones - Añadir campos calculados a cada objeto
        productos = cls.objects.annotate(
            valor_total=F('precio') * F('stock'),
            descuento=F('precio_base') - F('precio'),
            porcentaje_descuento=(F('precio_base') - F('precio')) * 100 / F('precio_base')
        )
        
        # Anotaciones con Count
        productos = cls.objects.annotate(
            num_reviews=Count('review'),
            num_ventas=Count('venta')
        )
        
        # Anotaciones con Case/When (if/else condicionales)
        from django.db.models import Case, When, Value, IntegerField
        
        productos = cls.objects.annotate(
            estado_stock=Case(
                When(stock=0, then=Value('Agotado')),
                When(stock__lt=10, then=Value('Bajo')),
                When(stock__lt=50, then=Value('Medio')),
                default=Value('Alto'),
                output_field=CharField()
            )
        )
        
        # Agrupación (GROUP BY)
        from django.db.models.functions import ExtractYear, ExtractMonth
        
        # Ventas por año y mes
        ventas_por_mes = cls.objects.annotate(
            año=ExtractYear('fecha_venta'),
            mes=ExtractMonth('fecha_venta')
        ).values('año', 'mes').annotate(
            total_ventas=Sum('cantidad'),
            ingresos=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('año', 'mes')
        
        # Concatenación de campos
        from django.db.models.functions import Concat
        from django.db.models import Value
        
        productos = cls.objects.annotate(
            nombre_completo=Concat(
                'nombre', Value(' - '), 'marca', Value(' ('), 'categoria__nombre', Value(')')
            )
        )
        
        return "Ejemplos de consultas avanzadas de QuerySets"
```

## 14. Consultas y joins complejos

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    
    @classmethod
    def consultas_complejas(cls):
        # select_related - Para relaciones ForeignKey y OneToOne
        productos = cls.objects.select_related('categoria', 'marca')
        
        # Ahora podemos acceder a producto.categoria.nombre sin consultas adicionales
        for producto in productos:
            print(f"{producto.nombre} - {producto.categoria.nombre}")
        
        # prefetch_related - Para relaciones ManyToMany y "relaciones inversas"
        productos = cls.objects.prefetch_related('etiquetas', 'reviews')
        
        # Prefetch con Prefetch - Para personalizar la consulta prefetch
        from django.db.models import Prefetch
        
        productos = cls.objects.prefetch_related(
            Prefetch(
                'reviews',
                queryset=Review.objects.filter(rating__gte=4).select_related('usuario'),
                to_attr='buenas_reviews'
            )
        )
        
        # Consultas complejas con select_related + prefetch_related
        productos = cls.objects.select_related(
            'categoria', 'marca'
        ).prefetch_related(
            'etiquetas',
            Prefetch('reviews', queryset=Review.objects.select_related('usuario'))
        )
        
        # Consultas con joins explícitos
        from django.db.models import OuterRef, Subquery
        
        # Subconsulta - Última review de cada producto
        ultima_review = Review.objects.filter(
            producto=OuterRef('pk')
        ).order_by('-fecha_creacion').values('texto')[:1]
        
        productos = cls.objects.annotate(
            ultima_review=Subquery(ultima_review)
        )
        
        # Consultas en bruto (raw SQL)
        productos = cls.objects.raw("""
            SELECT p.*, c.nombre as categoria_nombre
            FROM producto p
            JOIN categoria c ON p.categoria_id = c.id
            WHERE p.precio > 100
            ORDER BY p.nombre
        """)
        
        # Usando extra() para añadir JOIN, WHERE o SELECT
        productos = cls.objects.extra(
            select={'categoria_nombre': 'categoria.nombre'},
            tables=['categoria'],
            where=['producto.categoria_id = categoria.id', 'producto.precio > 100']
        )
        
        return "Ejemplos de consultas y joins complejos"
```

## 15. Transacciones y operaciones atómicas

```python
from django.db import transaction

class Venta(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    
    @classmethod
    def realizar_venta(cls, producto_id, cantidad, cliente_id):
        # Transacción atómica decorando función
        @transaction.atomic
        def _realizar_venta():
            # Todo esto ocurre dentro de una transacción
            producto = Producto.objects.select_for_update().get(id=producto_id)
            
            if producto.stock < cantidad:
                raise ValueError("Stock insuficiente")
            
            # Actualizar stock
            producto.stock -= cantidad
            producto.save(update_fields=['stock'])
            
            # Crear venta
            venta = cls.objects.create(
                producto=producto,
                cantidad=cantidad,
                cliente_id=cliente_id
            )
            
            # Actualizar estadísticas
            ProductoEstadistica.objects.update_or_create(
                producto=producto,
                defaults={'total_vendido': F('total_vendido') + cantidad}
            )
            
            return venta
            
        return _realizar_venta()
    
    @classmethod
    def otro_ejemplo_transacciones(cls):
        # Usando with para bloques de transacción
        try:
            with transaction.atomic():
                # Todo dentro de este bloque es parte de la misma transacción
                producto1 = Producto.objects.select_for_update().get(id=1)
                producto1.stock -= 1
                producto1.save()
                
                producto2 = Producto.objects.select_for_update().get(id=2)
                producto2.stock -= 1
                
                if producto2.stock < 0:
                    # Si hay un error, toda la transacción se deshace
                    raise ValueError("Stock insuficiente para producto 2")
                    
                producto2.save()
        except Exception as e:
            # La transacción se ha deshecho, ningún cambio se guardó
            return f"Error en la transacción: {str(e)}"
        
        # Puntos de guardado (savepoints)
        with transaction.atomic():
            # Punto de guardado 1
            sid1 = transaction.savepoint()
            
            producto1 = Producto.objects.get(id=1)
            producto1.stock -= 1
            producto1.save()
            
            if alguna_condicion:
                # Deshacer hasta el punto de guardado 1
                transaction.savepoint_rollback(sid1)
            else:
                # Confirmar el punto de guardado 1
                transaction.savepoint_commit(sid1)
                
                # Punto de guardado 2
                sid2 = transaction.savepoint()
                
                try:
                    producto2 = Producto.objects.get(id=2)
                    producto2.stock -= 1
                    producto2.save()
                except:
                    # Deshacer hasta el punto de guardado 2
                    transaction.savepoint_rollback(sid2)
        
        return "Ejemplos de transacciones"
```

## 16. Índices, Constraints y Referencias complejas

```python
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    sku = models.CharField(max_length=20)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT,  # No permite eliminar categorías con productos
        related_name='productos'
    )
    proveedor = models.ForeignKey(
        'Proveedor',
        on_delete=models.SET_NULL,  # Permite eliminar proveedores, poniendo NULL
        null=True,
        blank=True
    )
    productos_relacionados = models.ManyToManyField(
        'self',              # Relación a sí mismo
        symmetrical=False,   # A->B no implica B->A
        blank=True
    )
    # Índices simples y compuestos (Django 2.2+)
    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria', 'precio']),
            models.Index(fields=['sku'], name='idx_producto_sku'),
            # Índice parcial solo para productos activos
            models.Index(
                fields=['nombre'],
                name='idx_producto_activo_nombre',
                condition=models.Q(activo=True)
            ),
            # Índice para búsqueda de texto
            models.Index(
                name='idx_producto_busqueda',
                fields=['nombre', 'descripcion'],
                opclasses=['varchar_pattern_ops', 'text_pattern_ops']
            ),
        ]
        
        # Constraints complejas (Django 2.2+)
        constraints = [
            # Restricción de unicidad 
            models.UniqueConstraint(
                fields=['sku', 'proveedor'],
                name='uq_producto_sku_proveedor'
            ),
            # Restricción de unicidad condicional
            models.UniqueConstraint(
                fields=['slug'],
                condition=models.Q(activo=True),
                name='uq_producto_activo_slug'
            ),
            # Restricción CHECK
            models.CheckConstraint(
                check=models.Q(precio__gt=0),
                name='chk_producto_precio_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(fecha_fin__gt=models.F('fecha_inicio')),
                name='chk_producto_fechas_validas'
            ),
        ]
```

## 17. Funciones de Búsqueda y Expresiones Avanzadas

```python
from django.db.models import F, Func, Value
from django.db.models.functions import Concat, Lower, Upper, Substr, Length, Replace, ExtractYear, Cast
from django.db.models import CharField, IntegerField, DateField

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def funciones_avanzadas(cls):
        # Operaciones con texto
        productos = cls.objects.annotate(
            # Concatenación
            titulo_completo=Concat(
                'nombre', Value(' - '), 'categoria__nombre',
                output_field=CharField()
            ),
            # Minúsculas y mayúsculas
            nombre_lower=Lower('nombre'),
            nombre_upper=Upper('nombre'),
            # Subcadenas
            primera_letra=Substr('nombre', 1, 1),
            # Longitud
            longitud_nombre=Length('nombre'),
            # Reemplazo
            sin_espacios=Replace('nombre', Value(' '), Value('_'))
        )
        
        # Operaciones con fecha
        productos = cls.objects.annotate(
            # Extraer componentes de fecha
            año=ExtractYear('fecha_creacion'),
            mes=ExtractMonth('fecha_creacion'),
            # Diferencia entre fechas
            dias_activo=Cast(
                Now() - F('fecha_creacion'),
                output_field=DurationField()
            )
        )
        
        # Funciones matemáticas
        from django.db.models.functions import Abs, Ceil, Floor, Round, Sin, Cos, Sqrt, Power
        
        productos = cls.objects.annotate(
            precio_redondeado=Round('precio'),
            precio_techo=Ceil('precio'),
            precio_suelo=Floor('precio'),
            precio_absoluto=Abs('precio'),
            precio_raiz=Sqrt('precio'),
            precio_cuadrado=Power('precio', 2)
        )
        
        # Creando funciones personalizadas
        class GroupConcat(Func):
            function = 'GROUP_CONCAT'
            template = '%(function)s(%(expressions)s)'
            
        # Usando funciones SQL directamente
        from django.db.models.expressions import RawSQL
        
        productos = cls.objects.annotate(
            distancia=RawSQL(
                "ST_Distance(ubicacion, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
                (longitude, latitude)
            )
        ).order_by('distancia')
        
        return "Ejemplos de expresiones y funciones avanzadas"
```

## 18. Opciones de Definición de Modelos menos comunes

```python
class ProductoPersonalizado(models.Model):
    # Campo proxy que apunta a otro modelo pero con un nombre diferente
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.CASCADE,
        db_column='categoria_id',          # Nombre de columna en la BD
        to_field='codigo_categoria',       # Campo en Categoria (no es la PK)
        related_name='mis_productos',      # Nombre de la relación inversa
        related_query_name='mi_producto',  # Nombre para filtros inversos
        limit_choices_to={'activa': True}, # Limita las opciones disponibles
        swappable=True,                   # Si el modelo relacionado es intercambiable
    )
    
    # Definir un Manager de forma explícita con una función
    def productos_activos():
        return models.Manager().from_queryset(
            lambda self: self.filter(activo=True)
        )()
    
    activos = productos_activos()
    
    # Opciones menos comunes para campos
    codigo_promocional = models.CharField(
        max_length=10,
        db_collation='utf8_bin',            # Collation específica (sensible a mayúsculas/minúsculas)
        db_index=True,                      # Índice en la BD para este campo
    )
    
    # Campo con restricciones de BD pero sin restricciones en Python
    codigo_interno = models.CharField(
        max_length=50,
        db_column='internal_code',          # Nombre en la BD
        error_messages={                    # Mensajes de error personalizados
            'blank': 'Este campo no puede estar vacío.',
            'unique': 'Ya existe un producto con este código interno.'
        }
    )
    
    # Definir una PK personalizada
    codigo_unico = models.CharField(
        max_length=20,
        primary_key=True,                   # Este campo es la PK
        editable=False,                     # No se puede editar desde el admin
    )
    
    class Meta:
        # Definir permisos a nivel de modelo
        default_permissions = ('add', 'change', 'delete', 'view')
        permissions = [
            ('puede_publicar', 'Puede publicar productos'),
            ('puede_comprar', 'Puede comprar productos'),
        ]
        
        # Definir índice funcional
        indexes = [
            models.Index(
                Lower('nombre'),
                name='idx_lower_nombre'
            )
        ]
        
        # Controlar si Django maneja las tablas
        managed = True                      # Django gestiona esta tabla
        
        # Definir vistas de base de datos
        managed = False                     # Para usar con vistas de BD
        db_table = 'productos_activos_view' # Vista definida en la BD
```

## 19. Integración con otros sistemas y ORM avanzado

```python
# Integración con PostgreSQL - Campos específicos
from django.contrib.postgres.fields import ArrayField, HStoreField, JSONField
from django.contrib.postgres.search import SearchVectorField, SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.indexes import GinIndex

class ProductoPostgreSQL(models.Model):
    nombre = models.CharField(max_length=100)
    tags = ArrayField(
        models.CharField(max_length=50),
        size=10,                         # Limita a 10 elementos
        blank=True,                      # Permite array vacío
        default=list                     # Valor por defecto
    )
    atributos = HStoreField(default=dict)  # Diccionario clave-valor
    metadatos = JSONField(default=dict)   # Campo JSON
    
    # Para búsqueda de texto completo
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector'])  # Índice GIN para búsqueda rápida
        ]
    
    def save(self, *args, **kwargs):
        # Actualiza el vector de búsqueda al guardar
        self.search_vector = (
            SearchVector('nombre', weight='A') + 
            SearchVector('descripcion', weight='B')
        )
        super().save(*args, **kwargs)
    
    @classmethod
    def buscar(cls, consulta):
        search_query = SearchQuery(consulta)
        return cls.objects.annotate(
            rank=SearchRank(F('search_vector'), search_query)
        ).filter(
            search_vector=search_query
        ).order_by('-rank')
        
    @classmethod
    def consultas_especiales_postgres(cls):
        # Consulta en array (contiene elementos)
        productos = cls.objects.filter(tags__contains=['oferta', 'nuevo'])
        
        # Consulta en json/hstore
        productos = cls.objects.filter(metadatos__contains={'color': 'rojo'})
        productos = cls.objects.filter(metadatos__color='rojo')
        
        # Conteo de elementos array
        from django.contrib.postgres.aggregates import ArrayLength
        productos = cls.objects.annotate(
            num_tags=ArrayLength('tags', 1)  # 1 indica dimensión del array
        ).filter(num_tags__gt=3)
        
        return "Consultas especiales PostgreSQL"

# Modelos no mapeados directamente a tablas
class VentasReporte(models.Model):
    """Modelo para manejar reportes complejos sin tabla directa"""
    class Meta:
        managed = False  # No crea tabla
        
    @classmethod
    def ventas_por_mes(cls, año):
        """Obtiene datos que no corresponden a un solo modelo"""
        return Venta.objects.filter(
            fecha__year=año
        ).annotate(
            mes=ExtractMonth('fecha')
        ).values('mes').annotate(
            total=Sum('total')
        ).order_by('mes')
```
