from django.db import models
from authentication.models import CustomUser, Endereco
from django.core.validators import MinLengthValidator
from authentication.constants import (
    STATUS_CHOICES,
    ACTIVITY_CHOICES,
    TECNICAL_CHOICES,
    ATRASO_CHOICES,
)


class Cliente(models.Model):
    nome = models.CharField(max_length=50, validators=[MinLengthValidator(3)])
    rg = models.CharField(max_length=12, validators=[MinLengthValidator(3)])
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    telefone1 = models.CharField(max_length=14, validators=[MinLengthValidator(3)])
    telefone2 = models.CharField(max_length=14, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.nome


class OrdemDeServico(models.Model):
    ticket = models.CharField(max_length=200, unique=True)
    tecnico = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="ordens_técnico"
    )
    staff = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="ordens_staff"
    )
    descricao = models.TextField(max_length=600)
    previsao_chegada = models.DateTimeField()
    previsao_execucao = models.DateTimeField()
    material = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    equipamento = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    data_criacao = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    contrato = models.CharField(max_length=700, null=True, blank=True)
    atividade = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    status_tecnico = models.CharField(max_length=50, choices=TECNICAL_CHOICES)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="Aguardando"
    )
    atraso_em_minutos = models.CharField(max_length=50, null=True, blank=True, choices=ATRASO_CHOICES)
    atraso_descricao = models.TextField(max_length=400, null=True, blank=True)

    def __str__(self):
        return f"Ordem de Serviço #{self.pk}"


class HistoricoOsFinalizada(models.Model):
    ordem_de_servico = models.ForeignKey(
        OrdemDeServico, on_delete=models.CASCADE, related_name="historico_os"
    )
    data_finalizada = models.DateTimeField(auto_now_add=True)
    nome_responsavel = models.CharField(max_length=30, null=False)
    rg_responsavel = models.CharField(max_length=12, null=False)
    observacoes = models.TextField(max_length=400)
    foto = models.ImageField(upload_to="img/historico_os_finalizada/")

    def cliente_ticket_filename(instance, filename):
        ext = filename.split(".")[-1]
        return f"{instance.nome_responsavel}_{instance.ordem_de_servico.ticket}.{ext}"

    def save(self, *args, **kwargs):
        # Chama a função que define o caminho da imagem
        if self.foto:
            self.foto.name = self.cliente_ticket_filename(self.foto.name)
        super(HistoricoOsFinalizada, self).save(*args, **kwargs)
