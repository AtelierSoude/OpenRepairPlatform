# Generated by Django 3.2.2 on 2021-05-28 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0038_auto_20210526_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='allow_stuffs',
            field=models.BooleanField(blank=True, default=False, help_text='Les participants pourront déclarer leurs objets électroniques à réparer lors de la réservation', verbose_name='Souhaitez-vous gérer des réparations électroniques ?'),
        ),
        migrations.AlterField(
            model_name='historicalevent',
            name='allow_stuffs',
            field=models.BooleanField(blank=True, default=False, help_text='Les participants pourront déclarer leurs objets électroniques à réparer lors de la réservation', verbose_name='Souhaitez-vous gérer des réparations électroniques ?'),
        ),
    ]