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
    telefone1 = models.CharField(max_length=15, validators=[MinLengthValidator(3)])
    telefone2 = models.CharField(max_length=15, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.nome


class OrdemDeServico(models.Model):
    ticket = models.CharField(max_length=200, unique=True)
    tecnico = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ordens_técnico",
        null=True,
        default=None,
    )
    staff = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="ordens_staff"
    )
    descricao = models.TextField(max_length=600)
    previsao_chegada = models.DateTimeField(editable=True)
    previsao_execucao = models.DateTimeField(editable=True)
    material = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    equipamento = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    data_criacao = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    contrato = models.CharField(max_length=700, null=True, blank=True)
    atividade = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    status_tecnico = models.CharField(max_length=50, choices=TECNICAL_CHOICES)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="Aguardando"
    )
    atraso_em_minutos = models.CharField(max_length=50, choices=ATRASO_CHOICES)
    atraso_descricao = models.TextField(max_length=400)
    descricao_reagendamento = models.TextField(max_length=400)
    vezes_reagendada = models.IntegerField(default=0)
    aceite = models.BooleanField(default=False)

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
    video = models.FileField(
        upload_to="videos/historico_os_finalizada/", null=True, blank=True
    )

    # def cliente_ticket_filename(instance, filename):
    #     ext = filename.split(".")[-1]
    #     return f"{instance.nome_responsavel}_{instance.ordem_de_servico.ticket}.{ext}"

    # def save(self, *args, **kwargs):
    #     # Chama a função que define o caminho da imagem
    #     if self.foto:
    #         self.foto.name = self.cliente_ticket_filename(self.foto.name)
    #     if self.video:
    #         self.video.name = self.cliente_ticket_filename(self.video.name)
    #     super(HistoricoOsFinalizada, self).save(*args, **kwargs)


class Ocorrencia(models.Model):
    ordem_de_servico = models.ForeignKey(
        OrdemDeServico, on_delete=models.CASCADE, related_name="ocorrencias"
    )
    titulo = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    descricao = models.TextField(max_length=600)
    data_criacao = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to="img/ocorrencias/", null=True, blank=True)
    video = models.FileField(upload_to="videos/ocorrencias/", null=True, blank=True)

    def ticket_tecnico_ocorrencia(instance, filename):
        ext = filename.split(".")[-1]
        return f"{instance.ordem_de_servico.ticket} - {instance.ordem_de_servico.tecnico.first_name}{instance.ordem_de_servico.tecnico.first_name}.{ext}"

    def save(self, *args, **kwargs):
        # Chama a função que define o caminho da imagem
        if self.foto:
            self.foto.name = self.ticket_tecnico_ocorrencia(self.foto.name)
        if self.video:
            self.video.name = self.ticket_tecnico_ocorrencia(self.video.name)
        super(Ocorrencia, self).save(*args, **kwargs)

    def __str__(self):
        return f"Ocorrência para Ordem de Serviço #{self.ordem_de_servico.pk}"


class FotoHistorico(models.Model):
    historico = models.ForeignKey(
        "HistoricoOsFinalizada", on_delete=models.CASCADE, related_name="fotos"
    )
    foto = models.ImageField(
        upload_to="img/historico_os_finalizada/", null=True, blank=True
    )
