from django.shortcuts import render, redirect
from main.helpers import is_staff
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import OrdemDeServico
from .forms import (
    OrdemDeServicoForm,
    ClienteForm,
    ReagendarOrdemDeServicoForm,
    EscolherTecnicoForm,
)
from django.contrib import messages
from django.contrib.messages import constants
from authentication.forms import EnderecoForm
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime
from authentication.models import CustomUser
from geopy.distance import geodesic
from staff.helpers import obter_lat_lng_endereco, obter_lat_lng_tecnicos


@user_passes_test(is_staff)
def staff(request):
    try:
        staff = request.user
        ordens_em_atraso = OrdemDeServico.objects.filter(
            staff=staff,
            atraso_em_minutos__isnull=False,
            status__in=["Atenção", "Urgente", "Aguardando"],
            atraso_em_minutos__gt=0,
        )
        ordens_reagendar = OrdemDeServico.objects.filter(
            staff=staff,
            status="Reagendar",
        )
        total_reagendar = len(ordens_reagendar.values())

        atrasos = len(ordens_em_atraso.values())
        return render(
            request,
            "staff.html",
            {"atrasos": atrasos, "staff": staff, "total_reagendar": total_reagendar},
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def lista_os(request):
    try:
        staff = request.user
        ordens_em_atraso = OrdemDeServico.objects.filter(
            staff=staff,
            atraso_em_minutos__isnull=False,
            status__in=["Atenção", "Urgente", "Aguardando"],
            atraso_em_minutos__gt=0,
        )
        atrasos = len(ordens_em_atraso.values())
        data_atual = datetime.now().date()
        todas_as_ordens = OrdemDeServico.objects.filter(staff=staff)
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
                ordem.descricao_reagendamento = "Ordem ignorada pelo técnico"
                ordem.save()
        ordens = OrdemDeServico.objects.filter(
            staff=request.user,
            status__in=["Atenção", "Urgente", "Aguardando", "Concluído"],
        )
        ordens_reagendar = OrdemDeServico.objects.filter(
            staff=staff,
            status="Reagendar",
        )
        total_reagendar = len(ordens_reagendar.values())

        # Verifique se o parâmetro de pesquisa "buscar" está presente na solicitação GET
        filtros = request.GET.get("buscar")

        if filtros:
            try:
                data_filtrada = datetime.strptime(filtros, "%d-%m-%Y")
                ordens = ordens.filter(previsao_chegada__date=data_filtrada.date())
            except ValueError:
                # Lidar com o caso em que o filtro não é uma data válida
                pass
            else:
                # Se a conversão for bem-sucedida, filtre por data e ignore outros filtros
                items_per_page = 10
                paginator = Paginator(ordens, items_per_page)
                page = request.GET.get("page")

                try:
                    ordens = paginator.page(page)
                except PageNotAnInteger:
                    ordens = paginator.page(1)
                except EmptyPage:
                    ordens = paginator.page(paginator.num_pages)

                return render(
                    request,
                    "lista_os.html",
                    {
                        "ordens": ordens,
                        "atrasos": atrasos,
                        "total_reagendar": total_reagendar,
                    },
                )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})

    # Se não houver filtro por data, continue com os outros filtros
    if filtros:
        ordens = ordens.filter(
            Q(ticket__icontains=filtros)
            | Q(cliente__nome__icontains=filtros)
            | Q(status__icontains=filtros)
            | Q(endereco__cidade__icontains=filtros)
            | Q(endereco__rua__icontains=filtros)
            | Q(endereco__cep__icontains=filtros)
        )

    items_per_page = 10
    paginator = Paginator(ordens, items_per_page)
    page = request.GET.get("page")

    try:
        ordens = paginator.page(page)
    except PageNotAnInteger:
        ordens = paginator.page(1)
    except EmptyPage:
        ordens = paginator.page(paginator.num_pages)

    return render(
        request,
        "lista_os.html",
        {
            "ordens": ordens,
            "atrasos": atrasos,
            "total_reagendar": total_reagendar,
        },
    )


@user_passes_test(is_staff)
def formulario_os(request):
    try:
        if request.method == "POST":
            os_form = OrdemDeServicoForm(request.POST)
            endereco_form = EnderecoForm(request.POST)
            if os_form.is_valid() and endereco_form.is_valid():
                ordem_de_servico = os_form.save(commit=False)
                ordem_de_servico.staff = request.user
                endereco = endereco_form.save()
                ordem_de_servico.endereco = endereco
                ordem_de_servico.status_tecnico = "Aguardando Aceite"
                ordem_de_servico.save()
                messages.add_message(request, constants.SUCCESS, "Dados salvos!")
                return redirect("lista_os_sem_tecnico")
            else:
                messages.add_message(request, constants.ERROR, "Formulário inválido")
                return redirect("formulario_os")
        else:
            os_form = OrdemDeServicoForm()
            endereco_form = EnderecoForm()
        return render(
            request,
            "formulario_os.html",
            {
                "os_form": os_form,
                "endereco_form": endereco_form,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})

@user_passes_test(is_staff)
def update_tecnico(request, ordem_id):
    try:
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
        lat_long_ordem = obter_lat_lng_endereco(ordem.endereco)
        tecnicos = CustomUser.objects.filter(groups__name="Técnico")

        # Calcular distância entre a ordem e cada técnico usando geopy
        distancias = {}
        for tecnico in tecnicos:
            lat_long_tecnico = obter_lat_lng_endereco(tecnico.endereco)
            distancia = geodesic(lat_long_ordem, lat_long_tecnico).kilometers
            distancias[tecnico] = distancia

        # Ordenar os técnicos pela distância e selecionar os 10 mais próximos
        tecnicos_ordenados = sorted(distancias.items(), key=lambda x: x[1])[:10]

        if request.method == "POST":
            form = EscolherTecnicoForm(request.POST)
            if form.is_valid():
                ordem.tecnico = form.cleaned_data["tecnico"]
                ordem.save()
                messages.add_message(
                    request, constants.SUCCESS, "Técnico associado à ordem com sucesso!"
                )
                return redirect("formulario_os")
        else:
            form = EscolherTecnicoForm()

        return render(
            request,
            "update_tecnico.html",
            {
                "form": form,
                "ordem_id": ordem_id,
                "ordem": ordem,
                "tecnicos": tecnicos,
                "tecnicos_proximos": tecnicos_ordenados,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def lista_os_sem_tecnico(request):
    try:
        staff = request.user
        ordens = OrdemDeServico.objects.filter(staff=staff, tecnico__isnull=True)
        return render(request, "lista_os_sem_tecnico.html", {"ordens": ordens})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def formulario_cliente(request):
    try:
        if request.method == "POST":
            cliente_form = ClienteForm(request.POST)

            if cliente_form.is_valid():
                cliente = cliente_form.save(commit=False)
                cliente.save()
                messages.add_message(
                    request, constants.SUCCESS, "Dados cadastrados com sucesso"
                )
                return redirect("formulario_cliente")
            else:
                messages.add_message(request, constants.ERROR, "Formulário inválido")

        else:
            cliente_form = ClienteForm()

        return render(
            request,
            "formulario_cliente.html",
            {
                "cliente_form": cliente_form,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def ordens_em_atraso(request):
    try:
        # Recupere todas as ordens de serviço do usuário staff logado que tenham atraso
        staff = request.user
        ordens_em_atraso = OrdemDeServico.objects.filter(
            staff=staff,
            atraso_em_minutos__isnull=False,
            atraso_em_minutos__gt=0,
            status__in=["Atenção", "Urgente", "Aguardando"],
        )
        atrasos = ordens_em_atraso.count()

        ordens_reagendar = OrdemDeServico.objects.filter(
            staff=staff,
            status="Reagendar",
        )
        total_reagendar = ordens_reagendar.count()

        return render(
            request,
            "ordens_em_atraso.html",
            {
                "ordens_em_atraso": ordens_em_atraso,
                "staff": staff,
                "atrasos": atrasos,
                "total_reagendar": total_reagendar,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def reagendar_staff(request):
    try:
        staff = request.user
        ordens_em_atraso = OrdemDeServico.objects.filter(
            staff=staff,
            atraso_em_minutos__isnull=False,
            status__in=["Atenção", "Urgente", "Aguardando"],
            atraso_em_minutos__gt=0,
        )
        atrasos = len(ordens_em_atraso.values())
        ordens_reagendar = OrdemDeServico.objects.filter(
            staff=staff,
            status="Reagendar",
        )
        total_reagendar = len(ordens_reagendar.values())
        print("weeee", ordens_reagendar)
        return render(
            request,
            "reagendar_staff.html",
            {
                "ordens_reagendar": ordens_reagendar,
                "staff": staff,
                "total_reagendar": total_reagendar,
                "atrasos": atrasos,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def update_reagendar(request, ordem_id):
    try:
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
        if ordem.atraso_em_minutos:
            ordem.atraso_em_minutos = ""
            ordem.atraso_descricao = ""
            ordem.descricao_reagendamento = ""

        if request.method == "POST":
            form = ReagendarOrdemDeServicoForm(request.POST, instance=ordem)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, constants.SUCCESS, "Ordem reagendada com sucesso"
                )
                return redirect("reagendar_staff")
        else:
            form = ReagendarOrdemDeServicoForm(instance=ordem)

        return render(request, "update_reagendar.html", {"form": form, "ordem": ordem})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})
