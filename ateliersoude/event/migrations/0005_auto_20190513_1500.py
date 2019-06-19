# Generated by Django 2.2 on 2019-05-13 13:00

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_auto_20190506_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Event day'),
        ),
        migrations.AlterField(
            model_name='event',
            name='ends_at',
            field=models.TimeField(verbose_name='End date and time'),
        ),
        migrations.AlterField(
            model_name='event',
            name='starts_at',
            field=models.TimeField(default=django.utils.timezone.now, verbose_name='Start date and time'),
        ),
    ]