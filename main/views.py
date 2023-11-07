from django.shortcuts import render, redirect
from staff.forms import *
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from config import CHAVE_API_GOOGLE
from .helpers import *
from django.db.models import Q, Count, F, FloatField
from datetime import date, timedelta
from decimal import Decimal
from staff.models import OrdemDeServico
from authentication.forms import TelaUserForm


@user_passes_test(is_tecnico)
def minhas_os(request):
    try:
        status_filter = request.GET.get("status")
        previsao_chegada_filter = request.GET.get("previsao_chegada")

        hoje = date.today().strftime("%d.%m")
        ontem = (date.today() - timedelta(days=1)).strftime("%d.%m")

        user = request.user
        ordens_ativas = OrdemDeServico.objects.filter(
            tecnico=user, status__in=["Atenção", "Urgente", "Aguardando", "Concluído"]
        )

        if status_filter:
            ordens_ativas = ordens_ativas.filter(status=status_filter)
        if status_filter == "Todas":
            ordens_ativas = OrdemDeServico.objects.filter(
                tecnico=user,
                status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            )
        if previsao_chegada_filter:
            if previsao_chegada_filter == "Hoje":
                ordens_ativas = ordens_ativas.filter(previsao_chegada=date.today())
            elif previsao_chegada_filter == "Ontem":
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada=date.today() - timedelta(days=1)
                )
            elif previsao_chegada_filter == "Últimos 7 dias":
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada__date__gte=date.today() - timedelta(days=7)
                )
            elif previsao_chegada_filter == "Últimos 30 dias":
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada__date__gte=date.today() - timedelta(days=30)
                )

        return render(
            request,
            "minhas_os.html",
            {
                "ordens_de_servico": ordens_ativas,
                "user": user,
                "status_filter": status_filter,
                "previsao_chegada_filter": previsao_chegada_filter,
                "hoje": hoje,
                "ontem": ontem,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def home(request):
    try:
        return render(request, "home.html")
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@is_tecnico_and_owner
def os_detail(request, ordem_id):
    try:
        api_google_maps_key = CHAVE_API_GOOGLE
        user = request.user
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id, tecnico=user)
        if ordem.status == "Concluído":
            return HttpResponse("Ordem de Serviço já finalizada")
        status_ordem = ordem.status
        return render(
            request,
            "os_detail.html",
            {
                "ordem": ordem,
                "user": user,
                "status_ordem": status_ordem,
                "api_google_maps_key": api_google_maps_key,
            },
        )
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
        return render(
            request,
            "a_caminho.html",
            {"ordem": ordem, "user": user, "api_google_maps_key": api_google_maps_key},
        )
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
        return render(
            request,
            "no_local.html",
            {"ordem": ordem, "user": user},
        )
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

            return render(
                request,
                "finalizar_os.html",
                {"ordem": ordem, "user": user, "historico_form": historico_form},
            )

        elif request.method == "POST":
            historico_form = HistoricoOsFinalizadaForm(request.POST, request.FILES)
            if historico_form.is_valid():
                historico = historico_form.save(commit=False)
                ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
                ordem.status = "Concluído"
                ordem.save()
                historico.ordem_de_servico = ordem

                historico.save()

                return redirect("dashboard")
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
def os_finalizadas(request):
    try:
        user = request.user
        ordens_finalizadas = OrdemDeServico.objects.filter(
            tecnico=user, status="Concluído"
        )
        historicos = []
        for ordem in ordens_finalizadas:
            historicos_ordem = HistoricoOsFinalizada.objects.filter(
                ordem_de_servico=ordem
            )
            historicos.extend(historicos_ordem)
        return render(
            request,
            "os_finalizadas.html",
            {
                "ordens_finalizadas": ordens_finalizadas,
                "historicos": historicos,
                "user": user,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_tecnico)
def dashboard(request):
    try:
        status_filter = request.GET.get("status")

        user = request.user

        # Obtém a data de hoje e as datas de ontem, antes de ontem, 3 dias atrás e 4 dias atrás
        today = date.today()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)
        three_days_ago = today - timedelta(days=3)
        four_days_ago = today - timedelta(days=4)

        # Formate as datas no formato "DD/MM/YYYY"
        today_str = today.strftime("%d/%m/%Y")
        yesterday_str = yesterday.strftime("%d/%m/%Y")
        day_before_yesterday_str = day_before_yesterday.strftime("%d/%m/%Y")
        three_days_ago_str = three_days_ago.strftime("%d/%m/%Y")
        four_days_ago_str = four_days_ago.strftime("%d/%m/%Y")

        # Filtra todas as ordens ativas
        ordens_ativas = OrdemDeServico.objects.filter(
            tecnico=user, status__in=["Atenção", "Urgente", "Aguardando"]
        )
        ordens_ativas_hoje = OrdemDeServico.objects.filter(
            tecnico=user,
            previsao_chegada__date=today,
            status__in=["Atenção", "Urgente", "Aguardando"],
        )
        # Filtra todas as ordens finalizadas
        ordens_finalizadas = OrdemDeServico.objects.filter(
            tecnico=user, status__in=["Concluído"]
        )

        ordens_finalizadas_hoje = OrdemDeServico.objects.filter(
            tecnico=user, status__in=["Concluído"], previsao_chegada__date=today
        )

        # Filtra as ordens ativas com base nas datas de previsão de chegada
        ordens_ativas_today = ordens_ativas.filter(previsao_chegada__date=today)
        ordens_ativas_yesterday = ordens_ativas.filter(previsao_chegada__date=yesterday)
        ordens_ativas_day_before_yesterday = ordens_ativas.filter(
            previsao_chegada__date=day_before_yesterday
        )
        ordens_ativas_three_days_ago = ordens_ativas.filter(
            previsao_chegada__date=three_days_ago
        )
        ordens_ativas_four_days_ago = ordens_ativas.filter(
            previsao_chegada__date=four_days_ago
        )

        # Use a função annotate para contar a quantidade de ordens com cada status
        ordens_ativas_today = ordens_ativas_today.values("status").annotate(
            total=Count("status")
        )
        ordens_ativas_yesterday = ordens_ativas_yesterday.values("status").annotate(
            total=Count("status")
        )
        ordens_ativas_day_before_yesterday = ordens_ativas_day_before_yesterday.values(
            "status"
        ).annotate(total=Count("status"))
        ordens_ativas_three_days_ago = ordens_ativas_three_days_ago.values(
            "status"
        ).annotate(total=Count("status"))
        ordens_ativas_four_days_ago = ordens_ativas_four_days_ago.values(
            "status"
        ).annotate(total=Count("status"))

        if status_filter:
            # Se você ainda quiser filtrar por um status específico
            ordens_ativas_today = ordens_ativas_today.filter(status=status_filter)
            ordens_ativas_yesterday = ordens_ativas_yesterday.filter(
                status=status_filter
            )
            ordens_ativas_day_before_yesterday = (
                ordens_ativas_day_before_yesterday.filter(status=status_filter)
            )
            ordens_ativas_three_days_ago = ordens_ativas_three_days_ago.filter(
                status=status_filter
            )
            ordens_ativas_four_days_ago = ordens_ativas_four_days_ago.filter(
                status=status_filter
            )

        # Obtém o número total de ordens para cada dia
        total_ordens_today = ordens_ativas_today.aggregate(total=Count("id"))
        total_ordens_yesterday = ordens_ativas_yesterday.aggregate(total=Count("id"))
        total_ordens_day_before_yesterday = (
            ordens_ativas_day_before_yesterday.aggregate(total=Count("id"))
        )
        total_ordens_three_days_ago = ordens_ativas_three_days_ago.aggregate(
            total=Count("id")
        )
        total_ordens_four_days_ago = ordens_ativas_four_days_ago.aggregate(
            total=Count("id")
        )

        # Filtra todas as ordens de serviço sem filtro de status
        all_ordens = OrdemDeServico.objects.filter(tecnico=user)

        # Calcula o número de ordens de serviço para cada status
        counts = all_ordens.values("status").annotate(total=Count("status"))

        # Calcula o total de ordens de serviço
        total_ordens = all_ordens.count()

        # Inicializa as variáveis para armazenar a porcentagem de cada status
        percent_concluido = 0
        percent_atencao = 0
        percent_urgente = 0
        percent_aguardando = 0

        # Calcula a porcentagem de cada status em relação ao total de ordens
        for count in counts:
            if count["status"] == "Concluído":
                percent_concluido = round(
                    Decimal(count["total"]) / Decimal(total_ordens) * 100, 0
                )
            elif count["status"] == "Atenção":
                percent_atencao = round(
                    Decimal(count["total"]) / Decimal(total_ordens) * 100, 0
                )
            elif count["status"] == "Urgente":
                percent_urgente = round(
                    Decimal(count["total"]) / Decimal(total_ordens) * 100, 0
                )
            elif count["status"] == "Aguardando":
                percent_aguardando = round(
                    Decimal(count["total"]) / Decimal(total_ordens) * 100, 0
                )

        return render(
            request,
            "dashboard.html",
            {
                "ordens_ativas": ordens_ativas,
                "today": today_str,
                "yesterday": yesterday_str,
                "day_before_yesterday": day_before_yesterday_str,
                "three_days_ago": three_days_ago_str,
                "four_days_ago": four_days_ago_str,
                "ordens_ativas_today": ordens_ativas_today,
                "ordens_ativas_yesterday": ordens_ativas_yesterday,
                "ordens_ativas_day_before_yesterday": ordens_ativas_day_before_yesterday,
                "ordens_ativas_three_days_ago": ordens_ativas_three_days_ago,
                "ordens_ativas_four_days_ago": ordens_ativas_four_days_ago,
                "total_ordens_today": total_ordens_today["total"],
                "total_ordens_yesterday": total_ordens_yesterday["total"],
                "total_ordens_day_before_yesterday": total_ordens_day_before_yesterday[
                    "total"
                ],
                "total_ordens_three_days_ago": total_ordens_three_days_ago["total"],
                "total_ordens_four_days_ago": total_ordens_four_days_ago["total"],
                "user": user,
                "ordens_finalizadas": ordens_finalizadas,
                "percent_concluido": percent_concluido,
                "percent_atencao": percent_atencao,
                "percent_urgente": percent_urgente,
                "percent_aguardando": percent_aguardando,
                "ordens_ativas_hoje": ordens_ativas_hoje,
                "ordens_finalizadas_hoje": ordens_finalizadas_hoje,
            },
        )
    except Exception as e:
        # Tratamento de erro genérico
        # Ou personalize o tratamento de erro com base no tipo de exceção
        return render(request, "error.html", {"error_message": str(e)})


def tela_user(request):
    if request.method == "POST":
        user = request.user
        form = TelaUserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(
                "dashboard"
            )  # Redirecione para a página de perfil após a edição
    else:
        user = request.user
        form = TelaUserForm(instance=request.user)

    return render(request, "tela_user.html", {"form": form, "user": user})


def tela_busca(request):
    return render(request, "tela_busca.html")


def tela_busca_resultado(request):
    ordens = OrdemDeServico.objects.filter(tecnico=request.user)
    if "buscar" in request.GET:
        buscar_ticket = request.GET["buscar"]
        if buscar_ticket:
            ordens = ordens.filter(
                Q(ticket__icontains=buscar_ticket)
                | Q(cliente__nome__icontains=buscar_ticket)
            )

    return render(request, "tela_busca_resultado.html", {"ordens": ordens})
