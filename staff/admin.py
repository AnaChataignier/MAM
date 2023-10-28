from django.contrib import admin
from .models import OrdemDeServico, Endereco, HistoricoOsFinalizada, Cliente


admin.site.register(OrdemDeServico)
admin.site.register(Endereco)
admin.site.register(HistoricoOsFinalizada)
admin.site.register(Cliente)
