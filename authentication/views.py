from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .forms import CustomUserForm, EnderecoForm, CustomAuthenticationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.messages import constants


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
                return redirect("dashboard")  # Redireciona para a página de Técnico
            elif user.groups.filter(name="Staff").exists():
                return redirect("staff")  # Redireciona para a página de Staff

    else:
        form = CustomUserForm()
        endereco_form = EnderecoForm()
    return render(
        request, "register.html", {"form": form, "endereco_form": endereco_form}
    )


def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.groups.filter(name="Técnico").exists():
                    return redirect("dashboard")  # Redireciona para a página de Técnico
                elif user.groups.filter(name="Staff").exists():
                    return redirect("staff")  # Redireciona para a página de Staff
        else:
            messages.add_message(
                request, constants.ERROR, "Senha ou usuário incorretos"
            )
            return redirect("user_login")
    else:
        form = CustomAuthenticationForm()
    return render(request, "user_login.html", {"form": form})


def sair(request):
    logout(request)
    return redirect("user_login")
