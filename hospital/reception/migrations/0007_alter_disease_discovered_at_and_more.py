# Generated by Django 4.1.5 on 2023-01-26 14:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reception', '0006_alter_disease_discovered_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disease',
            name='discovered_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 26, 17, 44, 24, 730025)),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='receipt_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 26, 17, 44, 24, 730025)),
        ),
    ]
