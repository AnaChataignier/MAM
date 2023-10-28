from django.shortcuts import render, redirect
from staff.forms import *
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from config import CHAVE_API_GOOGLE
from .helpers import *




@user_passes_test(is_tecnico)
def minhas_ordens_de_servico(request):
    try:
        status_filter = request.GET.get("status")
        previsao_chegada_filter = request.GET.get("previsao_chegada")

        user = request.user
        ordens_ativas = OrdemDeServico.objects.filter(tecnico=user, status__in=["Atenção", "Urgente", "Aguardando"])

        if status_filter:
            ordens_ativas = ordens_ativas.filter(status=status_filter)
            
        if previsao_chegada_filter:
            ordens_ativas = ordens_ativas.filter(previsao_chegada=previsao_chegada_filter)

        return render(request, "minhas_ordens_de_servico.html", {
            "ordens_de_servico": ordens_ativas,
            "user": user,
            "status_filter": status_filter,
            "previsao_chegada_filter": previsao_chegada_filter })
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def home(request):
    try:
        return render(request, "home.html")
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})



@is_tecnico_and_owner
def ordens_detail(request, ordem_id):
    try:
        api_google_maps_key = CHAVE_API_GOOGLE
        user = request.user
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id, tecnico=user)
        if ordem.status == "Concluído":
            return HttpResponse("Ordem de Serviço já finalizada")
        status_ordem = ordem.status
        return render(
            request,"ordens_detail.html",{"ordem": ordem, "user": user, "status_ordem": status_ordem, "api_google_maps_key": api_google_maps_key,})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@is_tecnico_and_owner
def a_caminho(request, ordem_id):
    try:
        api_google_maps_key = CHAVE_API_GOOGLE
        user = request.user
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
        if ordem.status == "Concluído":
            return HttpResponse("Ordem de Serviço já finalizada")
        ordem.status_tecnico = "À Caminho"
        ordem.save()
        return render( request, "a_caminho.html", {"ordem": ordem, "user": user, "api_google_maps_key": api_google_maps_key},)
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@is_tecnico_and_owner
def no_local(request, ordem_id):
    try:
        user = request.user
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
        if ordem.status == "Concluído":
            return HttpResponse("Ordem de Serviço já finalizada")
        ordem.status_tecnico = "No Local"
        ordem.save()
        return render( request, "no_local.html", {"ordem": ordem, "user": user},)
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@is_tecnico_and_owner
def finalizar_os(request, ordem_id):
    try:
        if request.method == "GET":
            historico_form = HistoricoOsFinalizadaForm()
            user = request.user
            ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
            if ordem.status == "Concluído":
                return HttpResponse("Ordem de Serviço já finalizada")
            ordem.status_tecnico = "Finalizado"
            ordem.save()

            return render(request, "finalizar_os.html",{"ordem": ordem, "user": user, "historico_form": historico_form},)

        elif request.method == "POST":
            historico_form = HistoricoOsFinalizadaForm(request.POST, request.FILES)
            if historico_form.is_valid():
                historico = historico_form.save(commit=False)
                ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
                ordem.status = "Concluído"
                ordem.save()
                historico.ordem_de_servico = ordem

                historico.save()

                return redirect("minhas_ordens_de_servico")
            else:
                return render(
                    request,
                    "finalizar_os.html",
                    {"historico_form": historico_form},
                )
        return HttpResponse("Método não permitido")
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_tecnico)
def ordens_finalizadas(request):
    try:
        user = request.user
        ordens_finalizadas = OrdemDeServico.objects.filter(tecnico=user, status="Concluído")
        historicos = []
        for ordem in ordens_finalizadas:
            historicos_ordem = HistoricoOsFinalizada.objects.filter(ordem_de_servico=ordem)
            historicos.extend(historicos_ordem)
        return render(request, "ordens_finalizadas.html",
        {"ordens_finalizadas": ordens_finalizadas, "historicos": historicos,"user": user })
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})
