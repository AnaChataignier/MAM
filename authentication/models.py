from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from .constants import STATE_CHOICES
from django.core.files.storage import default_storage


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
    endereco = models.ForeignKey(
        Endereco, on_delete=models.CASCADE, null=True, default=None
    )
    foto = models.ImageField(upload_to="img/perfil_user/", null=True, blank=True)

    def cliente_profile_filename(instance, filename):
        ext = filename.split(".")[-1]
        return f"{instance.first_name}_{instance.last_name}_profile.{ext}"

    def save(self, *args, **kwargs):
        if self.pk:  # Verifique se o usuário já existe no banco de dados
            try:
                # Obtém a instância atual do usuário no banco de dados
                old_user = CustomUser.objects.get(pk=self.pk)
                if old_user.foto and self.foto != old_user.foto:
                    # Se a instância atual tiver uma foto diferente da anterior
                    # exclua a foto anterior
                    default_storage.delete(old_user.foto.name)
            except CustomUser.DoesNotExist:
                pass

        # Chama a função que define o caminho da nova imagem
        if self.foto:
            self.foto.name = self.cliente_profile_filename(self.foto.name)

        super(CustomUser, self).save(*args, **kwargs)
