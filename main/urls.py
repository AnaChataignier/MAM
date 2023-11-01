from django.urls import path
from . import views


urlpatterns = [
   
    path("minhas_os/",views.minhas_os,name="minhas_os",),
    path("os_detail/<int:ordem_id>",views.os_detail,name="os_detail"),
    path("a_caminho/<int:ordem_id>", views.a_caminho, name="a_caminho"),
    path("no_local/<int:ordem_id>", views.no_local, name="no_local"),
    path("finalizar_os/<int:ordem_id>", views.finalizar_os, name="finalizar_os"),
    path("os_finalizadas/", views.os_finalizadas, name="os_finalizadas"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
