from django.shortcuts import render, redirect
from main.helpers import is_staff
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from authentication.models import CustomUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import OrdemDeServico, Cliente
from .forms import OrdemDeServicoForm, ClienteForm
from django.contrib import messages
from django.contrib.messages import constants
from authentication.forms import EnderecoForm


@user_passes_test(is_staff)
def staff(request):
    try:
        user = request.user
        return render(request, "staff.html", {"user": user})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_staff)
def lista_os(request):
    status_filter = request.GET.get("status")
    tecnico_filter = request.GET.get("tecnico")
    data_chegada_min_filter = request.GET.get("data_chegada_min")
    data_chegada_max_filter = request.GET.get("data_chegada_max")

    users = CustomUser.objects.filter(groups__name="Técnico")

    ordens_de_servico = OrdemDeServico.objects.filter(staff=request.user)

    if status_filter:
        ordens_de_servico = ordens_de_servico.filter(status=status_filter)
    if tecnico_filter:
        ordens_de_servico = ordens_de_servico.filter(tecnico_id=tecnico_filter)
    if data_chegada_min_filter:
        try:
            data_chegada_min_filter = datetime.strptime(
                data_chegada_min_filter, "%Y-%m-%d"
            ).date()
            ordens_de_servico = ordens_de_servico.filter(
                previsao_chegada__gte=data_chegada_min_filter
            )
        except ValueError:
            pass

    if data_chegada_max_filter:
        try:
            data_chegada_max_filter = datetime.strptime(
                data_chegada_max_filter, "%Y-%m-%d"
            ).date()
            ordens_de_servico = ordens_de_servico.filter(
                previsao_chegada__lte=data_chegada_max_filter
            )
        except ValueError:
            pass

    items_per_page = 8
    paginator = Paginator(ordens_de_servico, items_per_page)
    page = request.GET.get("page")
    try:
        ordens_de_servico = paginator.page(page)
    except PageNotAnInteger:
        ordens_de_servico = paginator.page(1)
    except EmptyPage:
        ordens_de_servico = paginator.page(paginator.num_pages)

    return render(
        request,
        "lista_os.html",
        {
            "ordens_de_servico": ordens_de_servico,
            "users": users,
            "status_filter": status_filter,
            "tecnico_filter": tecnico_filter,
            "data_chegada_min_filter": data_chegada_min_filter,
            "data_chegada_max_filter": data_chegada_max_filter,
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
                return redirect("formulario_cliente")
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


def lista_clientes(request):
    nome_filter = request.GET.get("nome")
    telefone_filter = request.GET.get("telefone")
    rg_filter = request.GET.get("rg")
    estado_filter = request.GET.get("endereco")

    clientes = Cliente.objects.all()

    if nome_filter:
        clientes = clientes.filter(nome__icontains=nome_filter)

    if telefone_filter:
        clientes = clientes.filter(telefone1__icontains=telefone_filter)

    if rg_filter:
        clientes = clientes.filter(rg__icontains=rg_filter)

    if estado_filter:
        clientes = clientes.filter(
            cliente__endereco__estado__icontains=estado_filter
        )  # Substitua 'endereco_field' pelo campo correto no modelo de Endereço

    return render(
        request,
        "lista_clientes.html",
        {
            "clientes": clientes,
            "nome_filter": nome_filter,
            "telefone_filter": telefone_filter,
            "rg_filter": rg_filter,
            "estado_filter": estado_filter,
        },
    )


def lista_tecnicos(request):
    pass


def gerente(request):
    try:
        user = request.user
        return render(request, "gerente.html", {"user": user})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


def gerente_lista_os(request):
    status_filter = request.GET.get("status")
    tecnico_filter = request.GET.get("tecnico")
    data_chegada_min_filter = request.GET.get("data_chegada_min")
    data_chegada_max_filter = request.GET.get("data_chegada_max")

    users = CustomUser.objects.filter(groups__name="Técnico")

    ordens_de_servico = OrdemDeServico.objects.all()

    if status_filter:
        ordens_de_servico = ordens_de_servico.filter(status=status_filter)
    if tecnico_filter:
        ordens_de_servico = ordens_de_servico.filter(tecnico_id=tecnico_filter)
    if data_chegada_min_filter:
        try:
            data_chegada_min_filter = datetime.strptime(
                data_chegada_min_filter, "%Y-%m-%d"
            ).date()
            ordens_de_servico = ordens_de_servico.filter(
                previsao_chegada__gte=data_chegada_min_filter
            )
        except ValueError:
            pass

    if data_chegada_max_filter:
        try:
            data_chegada_max_filter = datetime.strptime(
                data_chegada_max_filter, "%Y-%m-%d"
            ).date()
            ordens_de_servico = ordens_de_servico.filter(
                previsao_chegada__lte=data_chegada_max_filter
            )
        except ValueError:
            pass

    items_per_page = 5
    paginator = Paginator(ordens_de_servico, items_per_page)
    page = request.GET.get("page")
    try:
        ordens_de_servico = paginator.page(page)
    except PageNotAnInteger:
        ordens_de_servico = paginator.page(1)
    except EmptyPage:
        ordens_de_servico = paginator.page(paginator.num_pages)

    return render(
        request,
        "gerente_lista_os.html",
        {
            "ordens_de_servico": ordens_de_servico,
            "users": users,
            "status_filter": status_filter,
            "tecnico_filter": tecnico_filter,
            "data_chegada_min_filter": data_chegada_min_filter,
            "data_chegada_max_filter": data_chegada_max_filter,
        },
    )


def ordens_em_atraso(request):
    # Recupere todas as ordens de serviço do usuário staff logado que tenham atraso
    staff = request.user
    ordens_em_atraso = OrdemDeServico.objects.filter(
        staff=staff, atraso_em_minutos__isnull=False
    )

    return render(
        request, "ordens_em_atraso.html", {"ordens_em_atraso": ordens_em_atraso, staff: "staff"}
    )
