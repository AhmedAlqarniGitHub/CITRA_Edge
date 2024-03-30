from django.shortcuts import render, redirect
from .models import Camera
from .forms import CameraForm
from .models import Server
from .forms import ServerForm


def index(request):
    return render(request, 'index.html')


def register_camera(request):
    if request.method == 'POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the index page or wherever appropriate
    else:
        form = CameraForm()

    return render(request, 'register_camera.html', {'form': form})

def register_server(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the index page or wherever appropriate
    else:
        form = ServerForm()

    return render(request, 'register_server.html', {'form': form})
