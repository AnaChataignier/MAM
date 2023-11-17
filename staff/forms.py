from django import forms
from .models import OrdemDeServico, HistoricoOsFinalizada, Ocorrencia
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
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    # tecnico = forms.ModelChoiceField(
    #     queryset=CustomUser.objects.filter(groups__name="Técnico"),
    #     empty_label="Selecione um técnico",
    # )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={"placeholder": "Selecione um cliente"}),
        empty_label="Selecione um cliente",
    )

    class Meta:
        model = OrdemDeServico
        exclude = [
            "endereco",
            "staff",
            "status_tecnico",
            "atraso_em_minutos",
            "atraso_descricao",
            "descricao_reagendamento",
            "vezes_reagendada",
            "tecnico",
        ]

    def __init__(self, *args, **kwargs):
        super(OrdemDeServicoForm, self).__init__(*args, **kwargs)

        # Remova a opção "Concluído" do campo de seleção status_tecnico
        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] not in ["Concluído", "Reagendar"]
        ]

        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"

        self.fields["ticket"].widget.attrs["placeholder"] = "Número ticket"
        self.fields["descricao"].widget.attrs["placeholder"] = "Descrição..."
        self.fields["material"].widget.attrs["placeholder"] = "Material"
        self.fields["equipamento"].widget.attrs["placeholder"] = "Equipamento"
        self.fields["contrato"].widget.attrs["placeholder"] = "Contrato"


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

        self.fields["nome_responsavel"].widget.attrs[
            "placeholder"
        ] = "Nome do Responsável"
        self.fields["rg_responsavel"].widget.attrs["placeholder"] = "RG"
        self.fields["observacoes"].widget.attrs["placeholder"] = "Observações..."


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"

        self.fields["nome"].widget.attrs["placeholder"] = "Nome"
        self.fields["rg"].widget.attrs["placeholder"] = "RG"
        self.fields["telefone1"].widget.attrs["placeholder"] = "Telefone 1"
        self.fields["telefone2"].widget.attrs["placeholder"] = "Telefone 2"


class GerenteClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"


class AtrasoForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ["atraso_em_minutos", "atraso_descricao"]

    def __init__(self, *args, **kwargs):
        super(AtrasoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class ReagendarForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ["descricao_reagendamento"]

    def __init__(self, *args, **kwargs):
        super(ReagendarForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class GerenteOrdemDeServicoForm(forms.ModelForm):
    tecnico = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(groups__name="Técnico"),
        empty_label="Selecione um técnico",
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={"placeholder": "Selecione um cliente"}),
        empty_label="Selecione um cliente",
    )

    class Meta:
        model = OrdemDeServico
        exclude = [
            "endereco",
            "status_tecnico",
            "atraso_em_minutos",
            "atraso_descricao",
            "vezes_reagendada",
            "descricao_reagendamento",
        ]

    def __init__(self, *args, **kwargs):
        super(GerenteOrdemDeServicoForm, self).__init__(*args, **kwargs)

        # Remova a opção "Concluído" do campo de seleção status_tecnico
        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] != "Concluído"
        ]

        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"

        self.fields["ticket"].widget.attrs["placeholder"] = "Número ticket"
        self.fields["tecnico"].widget.attrs["placeholder"] = "Técnico"
        self.fields["descricao"].widget.attrs["placeholder"] = "Descrição..."
        self.fields["material"].widget.attrs["placeholder"] = "Material"
        self.fields["equipamento"].widget.attrs["placeholder"] = "Equipamento"
        self.fields["contrato"].widget.attrs["placeholder"] = "Contrato"


class ReagendarOrdemDeServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ["previsao_chegada", "previsao_execucao", "status"]

    def __init__(self, *args, **kwargs):
        super(ReagendarOrdemDeServicoForm, self).__init__(*args, **kwargs)

        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] not in ["Concluído", "Reagendar"]
        ]

        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"


class EscolherTecnicoForm(forms.ModelForm):
    class Meta:
        model = OrdemDeServico
        fields = ["tecnico"]

    def __init__(self, *args, **kwargs):
        super(EscolherTecnicoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"

        self.fields["tecnico"].widget = forms.Select(attrs={"class": "form-control"})



class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ["titulo", "descricao", "foto"]

    def __init__(self, *args, **kwargs):
        super(OcorrenciaForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        self.fields["titulo"].widget.attrs["placeholder"] = "Título"
        self.fields["descricao"].widget.attrs[
            "placeholder"
        ] = "Descreva detalhadamente a ocorrência..."
