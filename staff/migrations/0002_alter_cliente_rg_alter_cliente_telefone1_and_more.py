# Generated by Django 4.2.6 on 2023-11-09 03:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("staff", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cliente",
            name="rg",
            field=models.CharField(
                max_length=12, validators=[django.core.validators.MinLengthValidator(3)]
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="telefone1",
            field=models.CharField(
                max_length=14, validators=[django.core.validators.MinLengthValidator(3)]
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="telefone2",
            field=models.CharField(
                max_length=14, validators=[django.core.validators.MinLengthValidator(3)]
            ),
        ),
    ]