# Generated by Django 4.2.6 on 2023-11-13 18:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("staff", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ordemdeservico",
            name="atraso_em_minutos",
            field=models.CharField(
                choices=[
                    ("", "Selecione"),
                    ("15", "15 minutos"),
                    ("30", "30 minutos"),
                    ("60", "1 hora"),
                    ("120", "2 horas"),
                    ("180", "3 horas"),
                ],
                default=django.utils.timezone.now,
                max_length=50,
            ),
            preserve_default=False,
        ),
    ]
