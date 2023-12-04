from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Endereco
import re
from django.contrib.auth.forms import AuthenticationForm


class CustomUserForm(UserCreationForm):
    GROUP_CHOICES = [
        ("Técnico", "Técnico")
    ]

    group = forms.ChoiceField(choices=GROUP_CHOICES)

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "telefone",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        self.fields["first_name"].widget.attrs["placeholder"] = "Nome"
        self.fields["last_name"].widget.attrs["placeholder"] = "Sobrenome"
        self.fields["telefone"].widget.attrs["placeholder"] = "Telefone"
        self.fields["email"].widget.attrs["placeholder"] = "Email"
        self.fields["password1"].widget.attrs["placeholder"] = "Senha"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirmação de Senha"
        self.fields["username"].widget.attrs["placeholder"] = "Usuário"
        

class EnderecoForm(forms.ModelForm):
    cep = forms.CharField(max_length=9, required=True)

    def clean_cep(self):
        cep = self.cleaned_data["cep"]
        if not re.match(r"^\d{5}-\d{3}$", cep):
            raise forms.ValidationError("CEP deve estar no formato XXXXX-XXX")
        return cep

    class Meta:
        model = Endereco
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EnderecoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        self.fields["cep"].widget.attrs["placeholder"] = "CEP"
        self.fields["bairro"].widget.attrs["placeholder"] = "Bairro"
        self.fields["rua"].widget.attrs["placeholder"] = "Rua"
        self.fields["cidade"].widget.attrs["placeholder"] = "Cidade"
        self.fields["estado"].widget.attrs["placeholder"] = "Estado"
        self.fields["numero"].widget.attrs["placeholder"] = "Numero"
        self.fields["complemento"].widget.attrs["placeholder"] = "Complemento"
        

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Usuário"
        self.fields["password"].widget.attrs["class"] = "form-control"
        self.fields["password"].widget.attrs["placeholder"] = "Senha"


class TelaUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["telefone", "email", "first_name", "last_name", "foto"]

    def __init__(self, *args, **kwargs):
        super(TelaUserForm, self).__init__(*args, **kwargs)

        # Adicione a classe 'form-control' a todos os campos do formulário
        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"
