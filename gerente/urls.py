from django.urls import path
from . import views

urlpatterns = [
    path("gerente/", views.gerente, name="gerente"),
    path("gerente_lista_os/", views.gerente_lista_os, name="gerente_lista_os"),
    path(
        "crud_gerente_os/<int:ordem_id>", views.crud_gerente_os, name="crud_gerente_os"
    ),
    path(
        "gerente_lista_clientes",
        views.gerente_lista_clientes,
        name="gerente_lista_clientes",
    ),
    path(
        "crud_gerente_clientes/<int:cliente_id>",
        views.crud_gerente_clientes,
        name="crud_gerente_clientes",
    ),
    path("gerente_lista_historico/", views.gerente_lista_historico, name="gerente_lista_historico"),
    path('deletar_os/<int:ordem_id>/', views.deletar_os, name='deletar_os'),
    path('deletar_cliente/<int:cliente_id>/', views.deletar_cliente, name='deletar_cliente'),
]
