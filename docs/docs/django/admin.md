# Guía Completa de Django Admin: De Básico a Avanzado

El Django Admin es una de las joyas de este framework, proporcionando una interfaz de administración generada automáticamente pero altamente personalizable. Esta guía cubre todas sus capacidades, desde lo más básico hasta técnicas avanzadas.

## 1. Introducción al Django Admin

Django Admin es una aplicación que genera automáticamente una interfaz de administración basada en tus modelos. Es perfecta para operaciones CRUD (Crear, Leer, Actualizar, Eliminar) internas sin necesidad de crear vistas personalizadas.

### Configuración inicial

El admin viene preinstalado en `INSTALLED_APPS` como `django.contrib.admin`. Para activarlo:

```python
# En urls.py
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Otras URLs...
]
```

### Creación de superusuario

Para acceder al admin necesitas crear un superusuario:

```bash
python manage.py createsuperuser
```

### Registro básico de modelos

```python
# En app/admin.py
from django.contrib import admin
from .models import MiModelo

admin.site.register(MiModelo)
```

Con esto mínimo, Django generará una interfaz completa para gestionar instancias de `MiModelo`.

## 2. Personalización Básica del Admin

### Usando decoradores

```python
# En app/admin.py
from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
```

### Opciones principales

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = ('nombre', 'precio', 'stock', 'categoria')
    
    # Controles para filtrar en la barra lateral
    list_filter = ('categoria', 'activo')
    
    # Campos por los que se puede buscar
    search_fields = ('nombre', 'descripcion')
    
    # Orden por defecto
    ordering = ('-fecha_creacion',)
    
    # Campos para edición rápida en la lista
    list_editable = ('precio', 'stock')
    
    # Controla cuántos elementos se muestran por página
    list_per_page = 25
    
    # Agrupación de campos en el formulario de edición/creación
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'descripcion', 'imagen')
        }),
        ('Información comercial', {
            'fields': ('precio', 'stock', 'categoria')
        }),
        ('Metadatos', {
            'classes': ('collapse',),  # Sección colapsable
            'fields': ('slug', 'activo', 'fecha_creacion'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('fecha_creacion',)
```

## 3. Personalización de la Visualización de Modelos

### Campos calculados o métodos como columnas

```python
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'get_total', 'estado')
    
    def get_total(self, obj):
        return f"${obj.total:.2f}"
    
    # Personalizar encabezado y ordenamiento
    get_total.short_description = 'Total Pedido'
    get_total.admin_order_field = 'total'  # Permite ordenar por este campo
```

### Personalización con HTML

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'estado_stock', 'miniatura')
    
    def estado_stock(self, obj):
        if obj.stock <= 0:
            return format_html('<span style="color: red;">Agotado</span>')
        if obj.stock < 10:
            return format_html('<span style="color: orange;">Bajo ({0})</span>', obj.stock)
        return format_html('<span style="color: green;">Disponible ({0})</span>', obj.stock)
    
    estado_stock.short_description = 'Estado del stock'
    
    def miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{0}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"
    
    miniatura.short_description = 'Imagen'
```

### Campos con enlace a detalles u otras páginas

```python
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_link', 'fecha', 'total')
    
    def cliente_link(self, obj):
        url = reverse('admin:clientes_cliente_change', args=[obj.cliente.id])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.nombre)
    
    cliente_link.short_description = 'Cliente'
    cliente_link.admin_order_field = 'cliente__nombre'  # Ordenar por nombre del cliente
```

## 4. Personalización de Formularios en el Admin

### Usando ModelForm personalizado

```python
from django import forms
from .models import Producto

class ProductoAdminForm(forms.ModelForm):
    descripcion_corta = forms.CharField(max_length=100, help_text="Versión corta para listados")
    
    class Meta:
        model = Producto
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        precio = cleaned_data.get('precio')
        costo = cleaned_data.get('costo')
        
        if precio and costo and precio < costo:
            raise forms.ValidationError("El precio no puede ser menor que el costo")
        
        return cleaned_data

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm
```

### Personalización avanzada de campos

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Usar widgets personalizados para campos específicos
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 4, 'cols': 40})},
        models.CharField: {'widget': forms.TextInput(attrs={'class': 'special'})},
    }
    
    # Personalizar un campo específico
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'descripcion':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 3})
        
        if db_field.name == 'categoria':
            kwargs['queryset'] = Categoria.objects.filter(activa=True)
            kwargs['empty_label'] = "Seleccione una categoría"
        
        return super().formfield_for_dbfield(db_field, **kwargs)
```

### Autocompletes para campos relacionales

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Para campos ForeignKey
    autocomplete_fields = ['categoria', 'marca']
    
    # Relacionados: en los modelos referenciados también debe configurarse
    search_fields = ['nombre', 'referencia']  # Necesario para que funcione como destino de autocomplete
```

## 5. Acciones Personalizadas

### Acción básica

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    actions = ['marcar_como_destacados', 'actualizar_precios']
    
    def marcar_como_destacados(self, request, queryset):
        queryset.update(destacado=True)
        self.message_user(request, f"{queryset.count()} productos marcados como destacados")
    
    marcar_como_destacados.short_description = "Marcar productos seleccionados como destacados"
```

### Acción con confirmación

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    actions = ['desactivar_productos']
    
    def desactivar_productos(self, request, queryset):
        if request.POST.get('post'):  # Confirmación recibida
            productos_actualizados = queryset.update(activo=False)
            self.message_user(request, f"{productos_actualizados} productos desactivados")
            return None
        
        # Mostrar página de confirmación
        context = {
            'queryset': queryset,
            'action': 'desactivar_productos',
            'title': 'Desactivar productos seleccionados',
            'content': f"¿Está seguro de querer desactivar {queryset.count()} productos?"
        }
        return render(request, 'admin/confirm_action.html', context)
    
    desactivar_productos.short_description = "Desactivar productos seleccionados"
```

El template `admin/confirm_action.html`:

```html
{% extends "admin/base_site.html" %}
{% block content %}
<h1>{{ title }}</h1>
<p>{{ content }}</p>
<form action="" method="post">
    {% csrf_token %}
    {% for obj in queryset %}
    <input type="hidden" name="_selected_action" value="{{ obj.pk }}" />
    {% endfor %}
    <input type="hidden" name="action" value="{{ action }}" />
    <input type="hidden" name="post" value="yes" />
    <input type="submit" value="Sí, estoy seguro" />
    <a href="{{ request.META.HTTP_REFERER }}" class="button cancel-link">No, cancelar</a>
</form>
{% endblock %}
```

### Acción con formulario

```python
class AjustarPreciosForm(forms.Form):
    porcentaje = forms.DecimalField(min_value=-100, max_value=100, decimal_places=2,
                                   help_text="Porcentaje para ajustar precios (positivo para aumentar, negativo para disminuir)")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    actions = ['ajustar_precios']
    
    def ajustar_precios(self, request, queryset):
        if 'apply' in request.POST:  # Formulario enviado
            form = AjustarPreciosForm(request.POST)
            if form.is_valid():
                porcentaje = form.cleaned_data['porcentaje']
                factor = 1 + (porcentaje / 100)
                
                # Usar F para actualización eficiente
                from django.db.models import F
                productos_actualizados = queryset.update(precio=F('precio') * factor)
                
                self.message_user(request, f"{productos_actualizados} productos actualizados. Precios {'+' if porcentaje > 0 else ''}{porcentaje}%")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = AjustarPreciosForm()
        
        # Mostrar formulario
        return render(request, 'admin/ajustar_precios.html', {
            'queryset': queryset,
            'form': form,
            'title': 'Ajustar precios',
        })
    
    ajustar_precios.short_description = "Ajustar precios de productos seleccionados"
```

Template `admin/ajustar_precios.html`:

```html
{% extends "admin/base_site.html" %}
{% block content %}
<h1>{{ title }}</h1>
<p>Ajustar precios para {{ queryset.count }} productos seleccionados.</p>
<form action="" method="post">
    {% csrf_token %}
    <div>
        {{ form.as_p }}
    </div>
    {% for obj in queryset %}
    <input type="hidden" name="_selected_action" value="{{ obj.pk }}" />
    {% endfor %}
    <input type="hidden" name="action" value="ajustar_precios" />
    <input type="submit" name="apply" value="Ajustar precios" />
    <a href="{{ request.META.HTTP_REFERER }}" class="button cancel-link">Cancelar</a>
</form>
{% endblock %}
```

## 6. Inlines (Modelos Relacionados)

### Configuración básica para relaciones uno a muchos

```python
class DetalleProductoInline(admin.TabularInline):
    model = DetalleProducto
    extra = 1  # Cuántas filas vacías mostrar
    
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    inlines = [DetalleProductoInline]
```

### Opciones avanzadas para inlines

```python
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    max_num = 5  # Número máximo de ítems
    min_num = 0  # Número mínimo de ítems
    verbose_name = "Imagen"
    verbose_name_plural = "Imágenes"
    can_delete = True
    show_change_link = True  # Muestra enlace al formulario de edición del modelo relacionado
    
    # Campos de solo lectura
    readonly_fields = ('thumbnail',)
    
    def thumbnail(self, obj):
        if obj.imagen:
            return format_html('<img src="{0}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"
```

### StackedInline vs TabularInline

```python
# Formato de apilado (más espacio, mejor para muchos campos)
class EspecificacionTecnicaInline(admin.StackedInline):
    model = EspecificacionTecnica
    extra = 1
    
# Formato de tabla (más compacto)
class ComentarioProductoInline(admin.TabularInline):
    model = ComentarioProducto
    extra = 0
```

### Inlines con formularios personalizados

```python
class VarianteProductoForm(forms.ModelForm):
    class Meta:
        model = VarianteProducto
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        # Validaciones personalizadas
        return cleaned_data

class VarianteProductoInline(admin.TabularInline):
    model = VarianteProducto
    form = VarianteProductoForm
    extra = 1
```

## 7. Admin Avanzado

### Filtros personalizados

```python
class PrecioRangoFilter(admin.SimpleListFilter):
    title = 'rango de precio'  # Título mostrado en el filtro
    parameter_name = 'precio_rango'  # Parámetro URL
    
    def lookups(self, request, model_admin):
        """Devuelve una lista de tuplas (valor, nombre) para los filtros"""
        return (
            ('bajo', 'Menos de $50'),
            ('medio', 'Entre $50 y $200'),
            ('alto', 'Más de $200'),
        )
    
    def queryset(self, request, queryset):
        """Filtra el queryset según el valor seleccionado"""
        if self.value() == 'bajo':
            return queryset.filter(precio__lt=50)
        if self.value() == 'medio':
            return queryset.filter(precio__gte=50, precio__lte=200)
        if self.value() == 'alto':
            return queryset.filter(precio__gt=200)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_filter = (PrecioRangoFilter, 'categoria', 'activo')
```

### Filtros relacionales anidados

```python
class CategoriaFiltro(admin.SimpleListFilter):
    title = 'categoría'
    parameter_name = 'categoria'
    
    def lookups(self, request, model_admin):
        categorias = Categoria.objects.filter(activa=True)
        return [(categoria.id, categoria.nombre) for categoria in categorias]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(categoria_id=self.value())

class MarcaFiltro(admin.SimpleListFilter):
    title = 'marca'
    parameter_name = 'marca'
    
    def lookups(self, request, model_admin):
        # Filtrar marcas según la categoría seleccionada
        categoria_id = request.GET.get('categoria')
        qs = Marca.objects.all()
        
        if categoria_id:
            qs = qs.filter(productos__categoria_id=categoria_id).distinct()
            
        return [(marca.id, marca.nombre) for marca in qs]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(marca_id=self.value())

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_filter = (CategoriaFiltro, MarcaFiltro)
```

### Búsqueda avanzada y búsqueda en campos relacionados

```python
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    search_fields = (
        'referencia',  # Búsqueda exacta
        'cliente__nombre',  # Búsqueda en campo de modelo relacionado
        'cliente__email',
        '^referencia_externa',  # Búsqueda que comienza con (startswith)
        '=telefono',  # Búsqueda exacta
        '@direccion',  # Búsqueda de texto completo (si la BD lo soporta)
    )
```

### Personalización del queryset mostrado

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        """Personalizar el queryset base del admin"""
        qs = super().get_queryset(request)
        
        # Prefetch y select_related para optimizar
        qs = qs.select_related('categoria', 'marca')
        
        # Filtrar según el usuario
        if not request.user.is_superuser:
            # Vendedores solo ven productos de sus categorías asignadas
            return qs.filter(categoria__in=request.user.categorias_asignadas.all())
        
        return qs
```

### Personalización de URLs en el admin

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'importar-productos/',
                self.admin_site.admin_view(self.importar_productos_view),
                name='importar-productos',
            ),
            path(
                'exportar-productos/',
                self.admin_site.admin_view(self.exportar_productos_view),
                name='exportar-productos',
            ),
        ]
        return custom_urls + urls
    
    def importar_productos_view(self, request):
        # Implementación de la vista personalizada
        context = {
            **self.admin_site.each_context(request),
            'title': 'Importar Productos',
            'form': ImportarProductosForm(),
        }
        return render(request, 'admin/importar_productos.html', context)
```

Para añadir enlace a la vista personalizada:

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # [...] other settings
    
    def changelist_view(self, request, extra_context=None):
        # Agregar botones para importar/exportar en la lista
        extra_context = extra_context or {}
        extra_context['import_url'] = reverse('admin:importar-productos')
        extra_context['export_url'] = reverse('admin:exportar-productos')
        return super().changelist_view(request, extra_context=extra_context)
```

## 8. Seguridad y Permisos

### Control de permisos básicos

Django incluye permisos por defecto para cada modelo: `add`, `change`, `delete` y `view`.

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Especifica qué permisos se requieren para acciones específicas
    def has_add_permission(self, request):
        # Solo administradores y gerentes pueden crear productos
        return request.user.is_superuser or request.user.groups.filter(name='Gerentes').exists()
    
    def has_change_permission(self, request, obj=None):
        # Verificar si puede editar este objeto específico
        if obj and obj.bloqueado:
            return request.user.is_superuser  # Solo superusuarios pueden editar productos bloqueados
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Nadie puede eliminar productos con ventas asociadas
        if obj and obj.tiene_ventas():
            return False
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        # Cualquier staff puede ver productos
        return request.user.is_staff
```

### Permisos personalizados

```python
# En tu models.py
class Producto(models.Model):
    # [...campos del modelo...]
    
    class Meta:
        permissions = [
            ('can_publish', 'Puede publicar productos'),
            ('can_feature', 'Puede destacar productos'),
            ('can_discount', 'Puede aplicar descuentos'),
        ]

# En tu admin.py
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    actions = ['publicar_productos', 'destacar_productos', 'aplicar_descuento']
    
    def publicar_productos(self, request, queryset):
        if not request.user.has_perm('productos.can_publish'):
            self.message_user(request, "No tienes permiso para publicar productos", level=messages.ERROR)
            return
        
        # Implementación
        queryset.update(publicado=True)
        self.message_user(request, f"{queryset.count()} productos publicados")
    
    # También puedes verificar permisos en otras partes:
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('productos.can_discount'):
            if 'aplicar_descuento' in actions:
                del actions['aplicar_descuento']
        return actions
```

### Filtrado de objetos por usuario

```python
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Superusuarios ven todo
        if request.user.is_superuser:
            return qs
        
        # Gerentes ven todos los pedidos de su tienda
        if request.user.groups.filter(name='Gerentes').exists():
            return qs.filter(tienda=request.user.tienda)
        
        # Vendedores solo ven sus propios pedidos
        return qs.filter(vendedor=request.user)
    
    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el vendedor actual si no está especificado
        if not change:  # Solo para nuevos objetos
            if not obj.vendedor:
                obj.vendedor = request.user
        
        super().save_model(request, obj, form, change)
```

### Campos visibles según permisos

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        # Si no tiene permiso de costo, eliminar la sección financiera
        if not request.user.has_perm('productos.view_financial'):
            return [fs for fs in fieldsets if fs[0] != 'Información financiera']
        
        return fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # Solo financieros pueden editar precios y costos
        if not request.user.groups.filter(name='Financieros').exists():
            readonly_fields.extend(['precio', 'costo', 'margen'])
        
        return readonly_fields
```

## 9. Optimización de Rendimiento

### Optimización de consultas

```python
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_select_related = ('cliente', 'tienda')  # Para ForeignKey y OneToOne
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Para relaciones inversas o ManyToMany
        qs = qs.prefetch_related('items', 'pagos')
        
        # Añadir anotaciones para valores calculados
        qs = qs.annotate(
            items_count=Count('items'),
            pagos_sum=Sum('pagos__monto')
        )
        
        return qs
```

### Paginación avanzada

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_per_page = 50  # Elementos por página
    list_max_show_all = 1000  # Máximo cuando se muestra "todo"
    show_full_result_count = False  # Evita consulta COUNT en tablas grandes
```

### Uso de cachés

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    def get_categoria_nombre(self, obj):
        # Usando caché de Django para optimizar
        from django.core.cache import cache
        
        cache_key = f"categoria_nombre_{obj.categoria_id}"
        nombre = cache.get(cache_key)
        
        if nombre is None:
            nombre = obj.categoria.nombre
            cache.set(cache_key, nombre, 3600)  # Caché por 1 hora
            
        return nombre
    
    get_categoria_nombre.short_description = "Categoría"
```

## 10. Personalización Completa de Templates

### Personalización del formulario de cambio

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    change_form_template = 'admin/productos/producto/change_form.html'
```

En `templates/admin/productos/producto/change_form.html`:

```html
{% extends "admin/change_form.html" %}
{% load i18n admin_urls static %}

{% block content %}
<div class="custom-header">
    <h2>Edición de {{ original.nombre }}</h2>
    <div class="stats">
        <p>Ventas: {{ original.total_ventas }}</p>
        <p>Valoración: {{ original.rating_promedio }}/5</p>
    </div>
</div>

{{ block.super }}  <!-- Contenido original del formulario -->

{% if original %}
<div class="custom-footer">
    <h3>Historial de cambios</h3>
    <ul>
        {% for log in original.get_historial %}
        <li>{{ log.timestamp }} - {{ log.user }}: {{ log.message }}</li>
        {% endfor %}
    </ul>
</div>
{% endif %}
{% endblock %}
```

### Personalización de la página de lista

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    change_list_template = 'admin/productos/producto/change_list.html'
```

En `templates/admin/productos/producto/change_list.html`:

```html
{% extends "admin/change_list.html" %}
{% load i18n admin_urls static %}

{% block object-tools-items %}
    <li>
        <a href="{% url 'admin:importar-productos' %}" class="btn btn-high">
            Importar productos
        </a>
    </li>
    <li>
        <a href="{% url 'admin:exportar-productos' %}" class="btn btn-high">
            Exportar productos
        </a>
    </li>
    {{ block.super }}
{% endblock %}

{% block result_list %}
    <div class="custom-stats">
        <h3>Resumen</h3>
        <ul>
            <li>Total productos: {{ cl.queryset.count }}</li>
            <li>Total en stock: {{ total_stock }}</li>
            <li>Valor inventario: ${{ valor_inventario }}</li>
        </ul>
    </div>
    {{ block.super }}
{% endblock %}
```

### Personalización de la página de eliminación

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    delete_confirmation_template = 'admin/productos/producto/delete_confirmation.html'
```

En el template:

```html
{% extends "admin/delete_confirmation.html" %}
{% load i18n admin_urls %}

{% block content %}
    <div class="alert alert-danger">
        <strong>¡Advertencia!</strong> Estás a punto de eliminar el producto {{ object }}.
        
        {% if associated_objects %}
        <p>Este producto tiene los siguientes objetos asociados que también serán eliminados:</p>
        <ul>
            {% for obj_type, objects in associated_objects.items %}
            <li>{{ obj_type }}: {{ objects|length }} {{ objects|pluralize }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    
    {{ block.super }}
{% endblock %}
```

## 11. Admin Extendido con Paquetes de Terceros

### Django Admin Interface

Para personalizar completamente la interfaz (colores, temas, logo):

```bash
pip install django-admin-interface
```

Agregar a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    # ...
]
```

### Django Import Export

Para importar/exportar datos en diferentes formatos (CSV, Excel, JSON):

```bash
pip install django-import-export
```

Integración:

```python
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ProductoResource(resources.ModelResource):
    class Meta:
        model = Producto
        import_id_fields = ('sku',)
        fields = ('sku', 'nombre', 'descripcion', 'precio', 'stock', 'categoria__nombre')
        export_order = ('sku', 'nombre', 'categoria__nombre', 'precio')

@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    resource_class = ProductoResource
```

### Django Admin Rangefilter

Para filtros de rango de fechas:

```bash
pip install django-admin-rangefilter
```

```python
from rangefilter.filters import DateRangeFilter

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_filter = (
        ('fecha_pedido', DateRangeFilter),
        'estado',
        'cliente',
    )
```

### Django Admin Actions

Para acciones masivas avanzadas:

```bash
pip install django-admin-actions
```

```python
from admin_actions.admin import ActionsModelAdmin

@admin.register(Producto)
class ProductoAdmin(ActionsModelAdmin):
    actions_list = ['action_duplicate', 'action_export_csv']
    
    def action_duplicate(self, request, queryset):
        for obj in queryset:
            obj.pk = None  # Crear copia
            obj.nombre = f"Copia de {obj.nombre}"
            obj.save()
            
        return f"{queryset.count()} elementos duplicados"
```

## 12. Buenas Prácticas

### Organización del código

```python
# admin.py limpio usando archivos separados

# En admin/__init__.py
from .producto import ProductoAdmin
from .pedido import PedidoAdmin
from .cliente import ClienteAdmin

from django.contrib import admin
from ..models import Producto, Pedido, Cliente

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Cliente, ClienteAdmin)

# En admin/producto.py
from django.contrib import admin
from ..models import Producto

class ProductoAdmin(admin.ModelAdmin):
    # Todas las configuraciones del admin aquí
```

### Decoradores para registrar métodos

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'estado_stock')
    
    @admin.display(description="Estado Stock", ordering='stock')
    def estado_stock(self, obj):
        if obj.stock <= 0:
            return "Agotado"
        elif obj.stock < 10:
            return f"Bajo ({obj.stock})"
        return f"Disponible ({obj.stock})"
```

### Admin personalizado a nivel de sitio

```python
# En myapp/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class MiSitioAdmin(AdminSite):
    site_header = _('Mi Empresa - Administración')
    site_title = _('Portal de Administración')
    index_title = _('Bienvenido al Portal')
    
    # Personalizar la vista de login
    login_template = 'admin/login_personalizado.html'
    
    # Personalizar la respuesta de index
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['estadisticas'] = obtener_estadisticas()
        return super().index(request, extra_context)

# Crear instancia de sitio personalizado
mi_admin_site = MiSitioAdmin(name='miadmin')

# Registrar modelos en el sitio personalizado
from .models import Producto, Categoria

@admin.register(Producto, site=mi_admin_site)
class ProductoAdmin(admin.ModelAdmin):
    # Configuración usual
    list_display = ('nombre', 'precio')

# En el archivo principal urls.py
from myapp.admin import mi_admin_site

urlpatterns = [
    path('miadmin/', mi_admin_site.urls),
    path('admin/', admin.site.urls),  # Mantener admin original o remover
]
```

### Administración de registros y páginas completas

Supongamos que queremos un panel de administración con estadísticas:

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    change_list_template = 'admin/productos/producto/change_list.html'
    
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        # Solo agregar estadísticas si no es error ni redirect
        if hasattr(response, 'context_data'):
            # Obtener queryset filtrado por los filtros aplicados
            qs = response.context_data['cl'].queryset
            
            extra_context = extra_context or {}
            extra_context.update({
                'total_productos': qs.count(),
                'total_stock': qs.aggregate(total=Sum('stock'))['total'] or 0,
                'valor_inventario': qs.aggregate(total=Sum(F('precio') * F('stock')))['total'] or 0,
                'categorias': Categoria.objects.annotate(
                    productos_count=Count('productos')
                ).order_by('-productos_count')[:5],
                'graficos_data': obtener_datos_graficos(qs),
            })
            response.context_data.update(extra_context)
        
        return response
```

### Integración con Django Rest Framework para API Admin

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.contrib import admin

# En api.py
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        return Response({
            'total': Producto.objects.count(),
            'total_activos': Producto.objects.filter(activo=True).count(),
            'valor_inventario': Producto.objects.filter(activo=True).aggregate(
                valor=Sum(F('precio') * F('stock'))
            )['valor'] or 0,
        })

# En admin.py
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    change_list_template = 'admin/productos/producto/change_list.html'
    
    # Añadir endpoints de la API al contexto
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['api_estadisticas_url'] = reverse('producto-estadisticas')
        return super().changelist_view(request, extra_context=extra_context)
```

En la plantilla, puedes usar JavaScript para consumir la API y mostrar datos dinámicos:

```html
{% extends "admin/change_list.html" %}
{% load static %}

{% block extrahead %}
{{ block.super }}
<script src="{% static 'admin/js/jquery.min.js' %}"></script>
<script src="{% static 'admin/js/chart.min.js' %}"></script>
<script>
$(document).ready(function() {
    // Consumir API desde JavaScript
    $.getJSON("{{ api_estadisticas_url }}", function(data) {
        // Actualizar estadísticas dinámicas
        $("#total_productos").text(data.total);
        $("#valor_inventario").text("$" + data.valor_inventario.toFixed(2));
        
        // Renderizar gráficos
        // ...
    });
});
</script>
{% endblock %}

{% block content %}
<div class="dashboard">
    <div class="stat-box">
        <h3>Total productos</h3>
        <div id="total_productos">Cargando...</div>
    </div>
    <div class="stat-box">
        <h3>Valor del inventario</h3>
        <div id="valor_inventario">Cargando...</div>
    </div>
    <div class="chart-container">
        <canvas id="productos-chart"></canvas>
    </div>
</div>
{{ block.super }}
{% endblock %}
```

## Conclusión y Resumen

El Django Admin es una herramienta extremadamente potente que puede adaptarse a casi cualquier necesidad de administración interna. Las claves principales para aprovecharlo al máximo son:

1. **Personalización incremental**: Comienza con el registro básico, luego personaliza la lista, luego los formularios, etc.
2. **Separación de responsabilidades**: Utiliza clases auxiliares como ModelForm, Resources, Filters, etc.
3. **Optimización**: Usa select_related, prefetch_related para evitar consultas N+1.
4. **Seguridad por capas**: Implementa permisos a nivel de modelo, objeto y campo.
5. **Extensibilidad**: No dudes en agregar vistas personalizadas para necesidades específicas.
6. **Reutilización**: Crea clases base con comportamiento compartido.