from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register_camera/', views.register_camera, name='register_camera'),
    path('register_server/', views.register_server, name='register_server'),
    # ...
]
