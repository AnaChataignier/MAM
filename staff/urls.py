from django.urls import path
from . import views

urlpatterns = [
    path("staff/", views.staff, name="staff"),
    path("lista_os/", views.lista_os, name="lista_os"),
    path("formulario_os/", views.formulario_os, name="formulario_os"),
    path("formulario_cliente/", views.formulario_cliente, name="formulario_cliente"),
    path("ordens_em_atraso/", views.ordens_em_atraso, name="ordens_em_atraso"),
    path("reagendar_staff/", views.reagendar_staff, name="reagendar_staff"),
    path(
        "update_reagendar/<int:ordem_id>",
        views.update_reagendar,
        name="update_reagendar",
    ),
]
