# Generated by Django 4.2.6 on 2023-11-11 00:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("staff", "0007_ordemdeservico_descricao_reagendamento_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordemdeservico",
            name="vezes_reagendada",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="ordemdeservico",
            name="status",
            field=models.CharField(
                choices=[
                    ("Reagendada", "Reagendada"),
                    ("Aguardando", "Aguardando"),
                    ("Atenção", "Atenção"),
                    ("Urgente", "Urgente"),
                    ("Concluído", "Concluído"),
                ],
                default="Aguardando",
                max_length=10,
            ),
        ),
    ]
