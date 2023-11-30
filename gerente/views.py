from django.shortcuts import render, get_object_or_404, redirect
from staff.models import OrdemDeServico, Cliente, HistoricoOsFinalizada
from staff.forms import ClienteForm, GerenteOrdemDeServicoForm
from django.contrib import messages
from django.contrib.messages import constants
from authentication.forms import EnderecoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from main.helpers import is_gerente


@user_passes_test(is_gerente)
def deletar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        messages.add_message(request, constants.SUCCESS, "Cliente deletado com sucesso")
        return redirect("gerente_lista_clientes")
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def gerente_lista_historico(request):
    try:
        historicos = HistoricoOsFinalizada.objects.prefetch_related("fotos").all()
        return render(
            request,
            "gerente_lista_historico.html",
            {
                "historicos": historicos,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def crud_gerente_clientes(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        if request.method == "POST":
            cliente_form = ClienteForm(request.POST, instance=cliente)
            endereco_form = EnderecoForm(request.POST, instance=cliente.endereco)

            if cliente_form.is_valid() and endereco_form.is_valid():
                cliente = cliente_form.save(commit=False)
                endereco = endereco_form.save()
                cliente.endereco = endereco
                cliente.save()

                return redirect("gerente_lista_clientes")
            else:
                return render(HttpResponse("Formulário inválido"))

        else:
            cliente_form = ClienteForm(instance=cliente)
            endereco_form = EnderecoForm(instance=cliente.endereco)

        return render(
            request,
            "crud_gerente_clientes.html",
            {
                "cliente_form": cliente_form,
                "endereco_form": endereco_form,
                "cliente": cliente,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def gerente_lista_clientes(request):
    try:
        clientes = Cliente.objects.all()
        if "buscar" in request.GET:
            filtros = request.GET["buscar"]
            if filtros:
                clientes = clientes.filter(
                    Q(nome__icontains=filtros)
                    | Q(endereco__cidade__icontains=filtros)
                    | Q(endereco__rua__icontains=filtros)
                    | Q(endereco__cep__icontains=filtros)
                )
        items_per_page = 15
        paginator = Paginator(clientes, items_per_page)
        page = request.GET.get("page")
        try:
            clientes = paginator.page(page)
        except PageNotAnInteger:
            clientes = paginator.page(1)
        except EmptyPage:
            clientes = paginator.page(paginator.num_pages)
        return render(
            request,
            "gerente_lista_clientes.html",
            {
                "clientes": clientes,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def crud_gerente_os(request, ordem_id):
    try:
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)

        if request.method == "POST":
            form = GerenteOrdemDeServicoForm(request.POST, instance=ordem)
            if form.is_valid():
                form.save()
                return redirect(
                    "gerente_lista_os"
                )  # Redireciona para a lista de ordens de serviço
        else:
            form = GerenteOrdemDeServicoForm(instance=ordem)

        return render(request, "crud_gerente_os.html", {"form": form, "ordem": ordem})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def deletar_os(request, ordem_id):
    try:
        ordem = get_object_or_404(OrdemDeServico, id=ordem_id)
        ordem.delete()
        messages.add_message(
            request, constants.SUCCESS, "Ordem de Serviço deletada com sucesso"
        )
        return redirect("gerente_lista_os")
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def gerente(request):
    try:
        user = request.user
        return render(request, "gerente.html", {"user": user})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})


@user_passes_test(is_gerente)
def gerente_lista_os(request):
    try:
        ordens = OrdemDeServico.objects.all()
        if "buscar" in request.GET:
            filtros = request.GET["buscar"]
            if filtros:
                ordens = ordens.filter(
                    Q(ticket__icontains=filtros)
                    | Q(cliente__nome__icontains=filtros)
                    | Q(status__icontains=filtros)
                    | Q(staff__first_name__icontains=filtros)
                    | Q(staff__last_name__icontains=filtros)
                    | Q(tecnico__first_name__icontains=filtros)
                    | Q(tecnico__last_name__icontains=filtros)
                    | Q(cliente__endereco__cidade__icontains=filtros)
                    | Q(cliente__endereco__rua__icontains=filtros)
                    | Q(cliente__endereco__cep__icontains=filtros)
                )

        items_per_page = 15
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
            "gerente_lista_os.html",
            {
                "ordens": ordens,
            },
        )
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})
