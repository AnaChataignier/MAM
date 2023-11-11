from django.shortcuts import render, redirect
from main.helpers import is_staff
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import OrdemDeServico
from .forms import OrdemDeServicoForm, ClienteForm, ReagendarOrdemDeServicoForm
from django.contrib import messages
from django.contrib.messages import constants
from authentication.forms import EnderecoForm
from django.db.models import Q
from django.shortcuts import get_object_or_404


@user_passes_test(is_staff)
def staff(request):
    staff = request.user
    ordens_em_atraso = OrdemDeServico.objects.filter(
        staff=staff,
        atraso_em_minutos__isnull=False,
        status__in=["Atenção", "Urgente", "Aguardando"],
    )
    ordens_reagendar = OrdemDeServico.objects.filter(
        staff=staff,
        status="Reagendar",
    )
    total_reagendar = len(ordens_reagendar.values())

    atrasos = len(ordens_em_atraso.values())

    try:
        return render(
            request,
            "staff.html",
            {"atrasos": atrasos, "staff": staff, "total_reagendar": total_reagendar},
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def lista_os(request):
    staff = request.user
    ordens_em_atraso = OrdemDeServico.objects.filter(
        staff=staff,
        atraso_em_minutos__isnull=False,
        status__in=["Atenção", "Urgente", "Aguardando"],
    )
    atrasos = len(ordens_em_atraso.values())
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
        ordens = ordens.filter(
            Q(ticket__icontains=filtros)
            | Q(cliente__nome__icontains=filtros)
            | Q(status__icontains=filtros)
            | Q(cliente__endereco__cidade__icontains=filtros)
            | Q(cliente__endereco__rua__icontains=filtros)
            | Q(cliente__endereco__cep__icontains=filtros)
        )

    items_per_page = 4
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
            if os_form.is_valid():
                ordem_de_servico = os_form.save(commit=False)
                ordem_de_servico.staff = request.user
                ordem_de_servico.status_tecnico = "Aguardando Aceite"
                ordem_de_servico.save()
                messages.add_message(
                    request, constants.SUCCESS, "Dados cadastrados com sucesso"
                )
                return redirect("formulario_os")
            else:
                messages.add_message(request, constants.ERROR, "Formulário inválido")
                return redirect("formulario_os")
        else:
            os_form = OrdemDeServicoForm()
        return render(
            request,
            "formulario_os.html",
            {
                "os_form": os_form,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def formulario_cliente(request):
    try:
        if request.method == "POST":
            cliente_form = ClienteForm(request.POST)
            endereco_form = EnderecoForm(request.POST)

            if cliente_form.is_valid() and endereco_form.is_valid():
                cliente = cliente_form.save(commit=False)
                endereco = endereco_form.save()
                cliente.endereco = endereco
                cliente.save()

                messages.add_message(
                    request, constants.SUCCESS, "Dados cadastrados com sucesso"
                )
                return redirect("formulario_cliente")
            else:
                messages.add_message(request, constants.ERROR, "Formulário inválido")

        else:
            cliente_form = ClienteForm()
            endereco_form = EnderecoForm()

        return render(
            request,
            "formulario_cliente.html",
            {
                "cliente_form": cliente_form,
                "endereco_form": endereco_form,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def ordens_em_atraso(request):
    # Recupere todas as ordens de serviço do usuário staff logado que tenham atraso
    staff = request.user
    ordens_em_atraso = OrdemDeServico.objects.filter(
        staff=staff,
        atraso_em_minutos__isnull=False,
        status__in=["Atenção", "Urgente", "Aguardando"],
    )
    atrasos = len(ordens_em_atraso.values())
    staff = request.user
    ordens_reagendar = OrdemDeServico.objects.filter(
        staff=staff,
        status="Reagendar",
    )
    total_reagendar = len(ordens_reagendar.values())

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


@user_passes_test(is_staff)
def reagendar_staff(request):
    staff = request.user
    ordens_em_atraso = OrdemDeServico.objects.filter(
        staff=staff,
        atraso_em_minutos__isnull=False,
        status__in=["Atenção", "Urgente", "Aguardando"],
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


def update_reagendar(request, ordem_id):
    ordem = get_object_or_404(OrdemDeServico, id=ordem_id)

    if request.method == "POST":
        form = ReagendarOrdemDeServicoForm(request.POST, instance=ordem)
        if form.is_valid():
            form.save()
            return redirect(
                "reagendar_staff"
            )  # Redireciona para a lista de ordens de serviço
    else:
        form = ReagendarOrdemDeServicoForm(instance=ordem)

    return render(request, "update_reagendar.html", {"form": form, "ordem": ordem})
