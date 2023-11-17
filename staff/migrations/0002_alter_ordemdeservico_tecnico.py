# Generated by Django 4.2.6 on 2023-11-16 22:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemdeservico',
            name='tecnico',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordens_técnico', to=settings.AUTH_USER_MODEL),
        ),
    ]
