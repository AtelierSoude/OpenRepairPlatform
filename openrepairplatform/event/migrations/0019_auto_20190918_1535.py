# Generated by Django 2.2.3 on 2019-09-18 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0018_auto_20190704_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='nedded_organizers',
            field=models.PositiveIntegerField(default=0, verbose_name='Needed organizers'),
        ),
        migrations.AddField(
            model_name='historicalevent',
            name='nedded_organizers',
            field=models.PositiveIntegerField(default=0, verbose_name='Needed organizers'),
        ),
    ]
