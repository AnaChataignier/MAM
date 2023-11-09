# Generated by Django 4.2.6 on 2023-11-09 18:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "staff",
            "0005_rename_nome_cliente_historicoosfinalizada_nome_responsavel_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="cliente",
            name="telefone1",
            field=models.CharField(
                max_length=15, validators=[django.core.validators.MinLengthValidator(3)]
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="telefone2",
            field=models.CharField(
                max_length=15, validators=[django.core.validators.MinLengthValidator(3)]
            ),
        ),
    ]
