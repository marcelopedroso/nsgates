# Generated by Django 5.1.6 on 2025-02-15 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_apikey_key_alter_historicalapikey_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalapikey',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalapikey',
            name='user',
        ),
        migrations.DeleteModel(
            name='APIKey',
        ),
        migrations.DeleteModel(
            name='HistoricalAPIKey',
        ),
    ]
