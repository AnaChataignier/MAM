from django.urls import path
from . import views

urlpatterns = [
    path("staff/", views.staff, name="staff"),
    path(
        "crud_gerente_os/<int:ordem_id>", views.crud_gerente_os, name="crud_gerente_os"
    ),
    path(
        "gerente_lista_clientes",
        views.gerente_lista_clientes,
        name="gerente_lista_clientes",
    ),
    path(
        "crud_gerente_clientes/<int:ordem_id>",
        views.crud_gerente_clientes,
        name="crud_gerente_clientes",
    ),
    path("lista_os/", views.lista_os, name="lista_os"),
    path("formulario_os/", views.formulario_os, name="formulario_os"),
    path("formulario_cliente/", views.formulario_cliente, name="formulario_cliente"),
    path("lista_clientes/", views.lista_clientes, name="lista_clientes"),
    path("gerente/", views.gerente, name="gerente"),
    path("gerente_lista_os/", views.gerente_lista_os, name="gerente_lista_os"),
    path("ordens_em_atraso/", views.ordens_em_atraso, name="ordens_em_atraso"),
]
