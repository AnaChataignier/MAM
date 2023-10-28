from django.urls import path
from .views import *

urlpatterns = [
       path("staff/", staff, name="staff"),
       path("lista_os/", lista_os, name="lista_os"),
       path("formulario_os/", formulario_os,name="formulario_os"),
       path("formulario_cliente/", formulario_cliente, name="formulario_cliente",),
]