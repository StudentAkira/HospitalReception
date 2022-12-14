# Generated by Django 4.1.3 on 2022-11-11 08:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reception', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='receipt_type',
            field=models.IntegerField(choices=[('30', 'Full receipt'), ('15', 'fast receipt receipt')], default='15'),
        ),
        migrations.AlterField(
            model_name='disease',
            name='discovered_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 11, 11, 0, 28, 783000)),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='receipt_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 11, 11, 0, 28, 782000)),
        ),
    ]
