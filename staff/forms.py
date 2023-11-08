from django import forms
from .models import OrdemDeServico, HistoricoOsFinalizada
from .models import Cliente
from authentication.models import CustomUser

# import re


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


class HistoricoOsFinalizadaForm(forms.ModelForm):
    class Meta:
        model = HistoricoOsFinalizada
        exclude = ["ordem_de_servico"]

    def __init__(self, *args, **kwargs):
        super(HistoricoOsFinalizadaForm, self).__init__(*args, **kwargs)

        # Adicione a classe 'form-control' a todos os campos do formulário
        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"

        self.fields["nome_cliente"].widget.attrs["placeholder"] = "Nome"
        self.fields["rg_cliente"].widget.attrs["placeholder"] = "RG"
        self.fields["observacoes"].widget.attrs["placeholder"] = "Observações..."


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ["endereco"]


class AtrasoForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ["atraso_em_minutos", "atraso_descricao"]

    def __init__(self, *args, **kwargs):
        super(AtrasoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
