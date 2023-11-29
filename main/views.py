from django.shortcuts import render, redirect
from staff.forms import (
    HistoricoOsFinalizadaForm,
    AtrasoForm,
    ReagendarForm,
    OcorrenciaForm,
)
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from config import CHAVE_API_GOOGLE
from .helpers import is_tecnico, is_tecnico_and_owner, calcula_aceite
from django.db.models import Q, Count
from decimal import Decimal
from staff.models import OrdemDeServico, HistoricoOsFinalizada
from authentication.forms import TelaUserForm
from datetime import date, timedelta, datetime, time
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Case, When, IntegerField


@user_passes_test(is_tecnico)
def minhas_os(request):
    try:
        status_filter = request.GET.get("status")
        previsao_chegada_filter = request.GET.get("previsao_chegada")

        user = request.user
        ordens_ativas = OrdemDeServico.objects.filter(
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        ).order_by("-previsao_chegada")
        ordens_ativas_counter = OrdemDeServico.objects.filter(
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )
        data_atual = datetime.now().date()
        todas_as_ordens = OrdemDeServico.objects.filter(tecnico=user)
        for ordem in todas_as_ordens:
            data_previsao = ordem.previsao_chegada.date()
            # Verifica as condições para alterar o status
            if data_previsao < data_atual and ordem.status in [
                "Atenção",
                "Urgente",
                "Aguardando",
            ]:
                # Atualiza o status e adiciona o motivo
                ordem.status = "Reagendar"
                ordem.status_tecnico = "Aguardando Aceite"
                ordem.vezes_reagendada += 1
                ordem.descricao_reagendamento = "Ordem ignorada pelo técnico"
                ordem.save()
        # Trate o filtro "Todas" separadamente
        if status_filter and status_filter != "Todas":
            ordens_ativas = ordens_ativas.filter(status=status_filter)

        if previsao_chegada_filter:
            if previsao_chegada_filter == "Hoje":
                start_of_day = datetime.combine(date.today(), time.min)
                end_of_day = datetime.combine(date.today(), time.max)
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada__range=(start_of_day, end_of_day)
                )
            elif previsao_chegada_filter == "Ontem":
                start_of_day = datetime.combine(
                    date.today() - timedelta(days=1), time.min
                )
                end_of_day = datetime.combine(
                    date.today() - timedelta(days=1), time.max
                )
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada__range=(start_of_day, end_of_day)
                )
            elif previsao_chegada_filter == "Últimos 7 dias":
                start_of_week = datetime.combine(
                    date.today() - timedelta(days=6), time.min
                )
                end_of_day = datetime.combine(date.today(), time.max)
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada__range=(start_of_week, end_of_day)
                )
            elif previsao_chegada_filter == "Últimos 30 dias":
                start_of_month = datetime.combine(
                    date.today() - timedelta(days=29), time.min
                )
                end_of_day = datetime.combine(date.today(), time.max)
                ordens_ativas = ordens_ativas.filter(
                    previsao_chegada__range=(start_of_month, end_of_day)
                )

        items_per_page = 5
        paginator = Paginator(ordens_ativas, items_per_page)
        page = request.GET.get("page")

        try:
            ordens_ativas = paginator.page(page)

        except PageNotAnInteger:
            ordens_ativas = paginator.page(1)
        except EmptyPage:
            ordens_ativas = paginator.page(paginator.num_pages)

        return render(
            request,
            "minhas_os.html",
            {"ordens_ativas": ordens_ativas, "qtdos": len(ordens_ativas_counter)},
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
        ordem = get_object_or_404(
            OrdemDeServico,
            id=ordem_id,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
        )
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
        ordem = get_object_or_404(
            OrdemDeServico,
            id=ordem_id,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
        )
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
        ordem = get_object_or_404(
            OrdemDeServico,
            id=ordem_id,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
        )

        # Obtém as ocorrências associadas à ordem de serviço
        ocorrencias = ordem.ocorrencias.all()

        if ordem.status == "Concluído":
            return HttpResponse("Ordem de Serviço já finalizada")

        ordem.status_tecnico = "No Local"
        ordem.save()

        return render(
            request,
            "no_local.html",
            {"ordem": ordem, "user": user, "ocorrencias": ocorrencias},
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@is_tecnico_and_owner
def finalizar_os(request, ordem_id):
    try:
        if request.method == "GET":
            historico_form = HistoricoOsFinalizadaForm()
            user = request.user
            ordem = get_object_or_404(
                OrdemDeServico,
                id=ordem_id,
                status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            )
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
                ordem = get_object_or_404(
                    OrdemDeServico,
                    id=ordem_id,
                    status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
                )
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
        user = request.user

        # Obtém a data de hoje e as datas de ontem, antes de ontem, 3 dias
        # atrás e 4 dias atrás
        today = date.today()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)
        three_days_ago = today - timedelta(days=3)
        four_days_ago = today - timedelta(days=4)

        # Formate as datas no formato "DD/MM/YYYY"
        day_before_yesterday_str = day_before_yesterday.strftime("%d/%m/%Y")
        three_days_ago_str = three_days_ago.strftime("%d/%m/%Y")
        four_days_ago_str = four_days_ago.strftime("%d/%m/%Y")

        # cards hoje
        card_total_realizadas_hoje = OrdemDeServico.objects.filter(
            previsao_chegada__date=today,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )

        card_realizadas_hoje = OrdemDeServico.objects.filter(
            previsao_chegada__date=today,
            status__in=["Concluído"],
            tecnico=user,
            aceite=True,
        )
        card_aguardando_hoje = OrdemDeServico.objects.filter(
            previsao_chegada__date=today,
            status__in=["Aguardando"],
            tecnico=user,
            aceite=True,
        )
        card_atencao_hoje = OrdemDeServico.objects.filter(
            previsao_chegada__date=today,
            status__in=["Atenção"],
            tecnico=user,
            aceite=True,
        )
        # card ontem
        card_total_realizadas_ontem = OrdemDeServico.objects.filter(
            previsao_chegada__date=yesterday,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )

        card_realizadas_ontem = OrdemDeServico.objects.filter(
            previsao_chegada__date=yesterday,
            status__in=["Concluído"],
            tecnico=user,
            aceite=True,
        )

        # card 2d
        card_total_realizadas_2d = OrdemDeServico.objects.filter(
            previsao_chegada__date=day_before_yesterday,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )

        card_realizadas_2d = OrdemDeServico.objects.filter(
            previsao_chegada__date=day_before_yesterday,
            status__in=["Concluído"],
            tecnico=user,
            aceite=True,
        )

        # card 3d
        card_total_realizadas_3d = OrdemDeServico.objects.filter(
            previsao_chegada__date=three_days_ago,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )

        card_realizadas_3d = OrdemDeServico.objects.filter(
            previsao_chegada__date=three_days_ago,
            status__in=["Concluído"],
            aceite=True,
            tecnico=user,
        )

        # card 4d
        card_total_realizadas_4d = OrdemDeServico.objects.filter(
            previsao_chegada__date=four_days_ago,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )

        card_realizadas_4d = OrdemDeServico.objects.filter(
            previsao_chegada__date=four_days_ago,
            status__in=["Concluído"],
            tecnico=user,
            aceite=True,
        )
        ordem_status = Case(
            When(status="Urgente", then=1),
            When(status="Atenção", then=2),
            When(status="Aguardando", then=3),
            default=4,
            output_field=IntegerField(),
        )

        # Proximas hoje
        proximas_hoje = OrdemDeServico.objects.filter(
            previsao_chegada__date=today,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando"],
            aceite=True,
        ).order_by(ordem_status)

        # Realizadas hoje
        realizadas_hoje = OrdemDeServico.objects.filter(
            previsao_chegada__date=today,
            tecnico=user,
            status__in=["Concluído"],
            aceite=True,
        )

        # Filtra todas as ordens de serviço de hoje
        all_ordens = OrdemDeServico.objects.filter(
            tecnico=user,
            previsao_chegada__date=today,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )

        # Calcula o número de ordens de serviço para cada status
        counts = all_ordens.values("status").annotate(total=Count("status"))

        # Calcula o total de ordens de serviço
        total_ordens = all_ordens.count()

        # Inicializa as variáveis para armazenar a porcentagem de cada status
        percent_concluido = 0
        percent_atencao = 0
        percent_urgente = 0
        percent_aguardando = 0

        # Calcula Aceite
        aceites = calcula_aceite(user)

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
                "day_before_yesterday": day_before_yesterday_str,
                "three_days_ago": three_days_ago_str,
                "four_days_ago": four_days_ago_str,
                "user": user,
                "percent_concluido": percent_concluido,
                "percent_atencao": percent_atencao,
                "percent_urgente": percent_urgente,
                "percent_aguardando": percent_aguardando,
                "card_total_realizadas_hoje": len(card_total_realizadas_hoje),
                "card_realizadas_hoje": len(card_realizadas_hoje),
                "card_aguardando_hoje": len(card_aguardando_hoje),
                "card_atencao_hoje": len(card_atencao_hoje),
                "card_total_realizadas_ontem": len(card_total_realizadas_ontem),
                "card_realizadas_ontem": len(card_realizadas_ontem),
                "card_total_realizadas_2d": len(card_total_realizadas_2d),
                "card_realizadas_2d": len(card_realizadas_2d),
                "card_total_realizadas_3d": len(card_total_realizadas_3d),
                "card_realizadas_3d": len(card_realizadas_3d),
                "card_total_realizadas_4d": len(card_total_realizadas_4d),
                "card_realizadas_4d": len(card_realizadas_4d),
                "proximas_hoje": proximas_hoje,
                "realizadas_hoje": realizadas_hoje,
                **aceites,
            },
        )
    except Exception as e:
        # Tratamento de erro genérico
        # Ou personalize o tratamento de erro com base no tipo de exceção
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_tecnico)
def tela_user(request):
    try:
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
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_tecnico)
def tela_busca(request):
    try:
        return render(request, "tela_busca.html")
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_tecnico)
def tela_busca_resultado(request):
    try:
        ordens = OrdemDeServico.objects.filter(
            tecnico=request.user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
            aceite=True,
        )
        if "buscar" in request.GET:
            buscar_ticket = request.GET["buscar"]
            if buscar_ticket:
                ordens = ordens.filter(
                    Q(ticket__icontains=buscar_ticket)
                    | Q(cliente__nome__icontains=buscar_ticket)
                    | Q(equipamento__icontains=buscar_ticket)
                    | Q(material__icontains=buscar_ticket)
                )

        return render(request, "tela_busca_resultado.html", {"ordens": ordens})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_tecnico)
def os_detail2(request, ordem_id):
    try:
        user = request.user
        ordem = get_object_or_404(
            OrdemDeServico,
            id=ordem_id,
            tecnico=user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
        )
        return render(
            request,
            "os_detail2.html",
            {
                "ordem": ordem,
                "user": user,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def os_detail3(request, ordem_id):
    user = request.user
    ordem = get_object_or_404(
        OrdemDeServico,
        id=ordem_id,
        tecnico=user,
        status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
    )
    return render(
            request,
            "os_detail3.html",
            {
                "ordem": ordem,
                "user": user,
            },
        )


def atraso(request, ordem_id):
    try:
        ordem = get_object_or_404(
            OrdemDeServico,
            id=ordem_id,
            status__in=["Atenção", "Urgente", "Aguardando"],
        )
        if request.method == "POST":
            form = AtrasoForm(request.POST, instance=ordem)
            if form.is_valid():
                form.save()
                redirect_url = reverse("a_caminho", args=[ordem.id])
                messages.add_message(request, constants.SUCCESS, "Atraso reportado")
                return redirect(redirect_url)
        else:
            form = AtrasoForm(instance=ordem)

        return render(request, "atraso.html", {"form": form, "ordem": ordem})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def reagendar(request, ordem_id):
    try:
        ordem = OrdemDeServico.objects.get(
            id=ordem_id, status__in=["Atenção", "Urgente", "Aguardando"], aceite=True
        )
        if request.method == "POST":
            ordem.status = "Reagendar"
            ordem.status_tecnico = "Aguardando Aceite"
            ordem.vezes_reagendada += 1
            form = ReagendarForm(request.POST, instance=ordem)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, constants.SUCCESS, "Ordem enviada para reagendamento"
                )
                redirect_url = reverse("dashboard")
                return redirect(redirect_url)
        else:
            form = ReagendarForm(instance=ordem)
        return render(request, "reagendar.html", {"ordem": ordem, "form": form})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def ocorrencias(request, ordem_id):
    try:
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)

        if request.method == "POST":
            form = OcorrenciaForm(request.POST, request.FILES)
            if form.is_valid():
                ocorrencia = form.save(commit=False)
                ocorrencia.ordem_de_servico = ordem
                ocorrencia.save()

                redirect_url = reverse("no_local", args=[ordem.id])
                return redirect(redirect_url)
        else:
            form = OcorrenciaForm()

        return render(request, "ocorrencias.html", {"form": form, "ordem": ordem})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def aceite(request):
    user = request.user
    ordens_pendentes = OrdemDeServico.objects.filter(
        aceite=False, tecnico=user, status__in=["Atenção", "Urgente", "Aguardando"]
    )
    data_atual = datetime.now().date()
    for ordem in ordens_pendentes:
        data_previsao = ordem.previsao_chegada.date()
        # Verifica as condições para alterar o status
        if data_previsao < data_atual and ordem.status in [
            "Atenção",
            "Urgente",
            "Aguardando",
        ]:
            # Atualiza o status e adiciona o motivo
            ordem.status = "Reagendar"
            ordem.status_tecnico = "Aguardando Aceite"
            ordem.vezes_reagendada += 1
            ordem.descricao_reagendamento = "Ordem ignorada pelo técnico"
            ordem.save()
    ordens_pendentes = OrdemDeServico.objects.filter(
        aceite=False, tecnico=user, status__in=["Atenção", "Urgente", "Aguardando"]
    )

    return render(
        request,
        "aceite.html",
        {"ordens_pendentes": ordens_pendentes, "qtdos": len(ordens_pendentes)},
    )


def aceitar_ordem(request, ordem_id):
    ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
    if request.method == "POST":
        ordem.aceite = True
        ordem.save()
        messages.add_message(request, constants.SUCCESS, "Ordem Aceita")
        return redirect("aceite")
    else:
        messages.warning(request, "Esta ordem já foi aceita anteriormente.")
    return redirect("aceite")


def recusar_ordem(request, ordem_id):
    ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
    if request.method == "POST":
        ordem.status = "Reagendar"
        ordem.status_tecnico = "Aguardando Aceite"
        ordem.vezes_reagendada += 1
        ordem.descricao_reagendamento = "Ordem recusada pelo técnico"
        ordem.save()
        messages.add_message(
            request, constants.SUCCESS, "Ordem enviada para reagendamento"
        )
        return redirect("aceite")
    return redirect("aceite")
