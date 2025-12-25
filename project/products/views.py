from .forms import ProductForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

# Create your views here.


@login_required
@permission_required('products.add_productmodel', raise_exception=True)
def create_product(request):
    context = {
        'form': ProductForm(),
    }
    if request.method == 'GET':
        return render(request, 'ProductForm.html', context)
    elif request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            # Auditoría
            form.instance.created_by = request.user
            form.instance.updated_by = request.user
            # Guardar el formulario
            form.save()
            messages.success(request, 'Product created successfully')
        else:
            messages.error(request, 'Error creating product')
        return render(request, 'ProductForm.html', {'form': form})
