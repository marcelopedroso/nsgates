# Generated by Django 5.1.6 on 2025-02-13 19:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_tokenintegration_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tokenintegration',
            name='user',
        ),
        migrations.DeleteModel(
            name='HistoricalTokenIntegration',
        ),
        migrations.DeleteModel(
            name='TokenIntegration',
        ),
    ]
