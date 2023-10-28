from django.shortcuts import render, redirect
from main.helpers import *
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from authentication.models import CustomUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.messages import constants



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
    tecnico_filter = request.GET.get("técnico")
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
            data_chegada_min_filter = datetime.strptime(data_chegada_min_filter, "%Y-%m-%d").date()
            ordens_de_servico = ordens_de_servico.filter( previsao_chegada__gte=data_chegada_min_filter)
        except ValueError:
            pass

    if data_chegada_max_filter:
        try:
            data_chegada_max_filter = datetime.strptime(data_chegada_max_filter, "%Y-%m-%d").date()
            ordens_de_servico = ordens_de_servico.filter(previsao_chegada__lte=data_chegada_max_filter)
        except ValueError:
            pass

    items_per_page = 20
    # Criando um objeto Paginator
    paginator = Paginator(ordens_de_servico, items_per_page)
    # Obter o número da página a partir dos parâmetros GET
    page = request.GET.get("page")
    try:
        # Obter a página atual
        ordens_de_servico = paginator.page(page)
    except PageNotAnInteger:
        # Se 'page' não for um número inteiro, mostre a primeira página
        ordens_de_servico = paginator.page(1)
    except EmptyPage:
        # Se 'page' estiver fora dos limites, mostre a última página
        ordens_de_servico = paginator.page(paginator.num_pages)

    return render(request,"lista_os.html",{"ordens_de_servico": ordens_de_servico, "users": users})



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

        return render(request,"formulario_cliente.html",{ "cliente_form": cliente_form,"endereco_form": endereco_form,})
    except Exception as e:
        return render(request, "error.html", {"error_message": str(e)})