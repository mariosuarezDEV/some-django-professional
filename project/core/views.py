from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
# Create your views here.


def login_view(request):
    if request.method == 'GET':
        # validar que el usuario no este autenticado
        if request.user.is_authenticated:
            # Redirigir a la página principal si ya está autenticado
            return HttpResponse("Already logged in", status=200)
        return render(request, 'LoginView.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            # Redirigir a la página principal después del inicio de sesión
            return HttpResponse("Login successful", status=200)
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
