from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserForm, EnderecoForm
from django.contrib.auth.models import Group


def register(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        endereco_form = EnderecoForm(request.POST)
        if form.is_valid() and endereco_form.is_valid():
            user = form.save(commit=False)
            endereco = endereco_form.save()
            user.endereco = endereco
            user.save()
            group_name = form.cleaned_data["group"]
            if group_name == "Staff":
                group = Group.objects.get(name="Staff")
            elif group_name == "Técnico":
                group = Group.objects.get(name="Técnico")
            user.groups.add(group)
            login(request, user)
            if user.groups.filter(name="Técnico").exists():
                return redirect("minhas_ordens_de_servico")  # Redireciona para a página de Técnico
            elif user.groups.filter(name="Staff").exists():
                return redirect("staff")  # Redireciona para a página de Staff
    else:
        form = CustomUserForm()
        endereco = EnderecoForm() 
    return render(request, "register.html", {"form": form, 'endereco':endereco})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.groups.filter(name="Técnico").exists():
                return redirect("minhas_ordens_de_servico")  # Redireciona para a página de Técnico
            elif user.groups.filter(name="Staff").exists():
                return redirect("staff")  # Redireciona para a página de Staff
    else:
        form = AuthenticationForm()
    return render(request, "user_login.html", {"form": form})


def sair(request):
    logout(request)
    return redirect("user_login")



