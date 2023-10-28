from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Endereco
import re

class CustomUserForm(UserCreationForm):
    GROUP_CHOICES = [
        ("Staff", "Staff"),
        ("Técnico", "Técnico"),
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