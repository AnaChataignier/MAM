from django.urls import path
from . import views


urlpatterns = [
   
    path("minhas_ordens_de_servico/",views.minhas_ordens_de_servico,name="minhas_ordens_de_servico",),
    path("ordens_detail/<int:ordem_id>",views.ordens_detail,name="ordens_detail"),
    path("a_caminho/<int:ordem_id>", views.a_caminho, name="a_caminho"),
    path("no_local/<int:ordem_id>", views.no_local, name="no_local"),
    path("finalizar_os/<int:ordem_id>", views.finalizar_os, name="finalizar_os"),
    path("ordens_finalizadas/", views.ordens_finalizadas, name="ordens_finalizadas"),
    path("", views.home, name="home"),
]
