from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from .constants import STATE_CHOICES



class Endereco(models.Model):
    cep = models.CharField(max_length=10)
    rua = models.CharField(max_length=30, validators=[MinLengthValidator(3)])
    bairro = models.CharField(max_length=20, validators=[MinLengthValidator(3)])
    cidade = models.CharField(max_length=20, validators=[MinLengthValidator(3)])
    estado = models.CharField(max_length=2, choices=STATE_CHOICES)
    numero = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    complemento = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.rua}, {self.numero}, {self.complemento}, {self.bairro}, {self.cidade}, {self.estado}, CEP: {self.cep}"


class CustomUser(AbstractUser):
    telefone = models.CharField(max_length=15, null=False)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, null=True, default=None)


