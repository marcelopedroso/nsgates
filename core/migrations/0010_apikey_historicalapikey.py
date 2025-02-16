# Generated by Django 5.1.6 on 2025-02-15 02:44

import django.db.models.deletion
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_historicalapikey_history_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(help_text='Nome do serviço/sistema que usará a API Key.', max_length=255, unique=True, verbose_name='Nome')),
                ('key', models.CharField(editable=False, max_length=64, unique=True, verbose_name='Chave de API')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Defina uma data de expiração opcional.', null=True, verbose_name='Expira em')),
                ('revoked', models.BooleanField(default=False, help_text='Se marcado, a API Key não será mais válida.', verbose_name='Revogado')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalAPIKey',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(db_index=True, help_text='Nome do serviço/sistema que usará a API Key.', max_length=255, verbose_name='Nome')),
                ('key', models.CharField(db_index=True, editable=False, max_length=64, verbose_name='Chave de API')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Defina uma data de expiração opcional.', null=True, verbose_name='Expira em')),
                ('revoked', models.BooleanField(default=False, help_text='Se marcado, a API Key não será mais válida.', verbose_name='Revogado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical api key',
                'verbose_name_plural': 'historical api keys',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
