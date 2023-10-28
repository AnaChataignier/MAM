from django import forms
from .models import OrdemDeServico, HistoricoOsFinalizada
from .models import Endereco, Cliente
from authentication.models import CustomUser
import re


class OrdemDeServicoForm(forms.ModelForm):
    previsao_chegada = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    previsao_execucao = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%mT%H:%M"],
    )
    tecnico = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(groups__name="Técnico")
    )

    class Meta:
        model = OrdemDeServico
        exclude = ["endereco", "staff", "status_tecnico"]

    def __init__(self, *args, **kwargs):
        super(OrdemDeServicoForm, self).__init__(*args, **kwargs)

        # Remova a opção "Concluído" do campo de seleção status_tecnico
        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] != "Concluído"
        ]


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


class HistoricoOsFinalizadaForm(forms.ModelForm):
    class Meta:
        model = HistoricoOsFinalizada
        exclude = ["ordem_de_servico"]


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ["endereco"]
