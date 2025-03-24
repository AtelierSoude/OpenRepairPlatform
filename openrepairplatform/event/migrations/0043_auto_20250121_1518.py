# Generated by Django 3.2.2 on 2025-01-21 14:18

from django.db import migrations
import openrepairplatform.fields


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0042_alter_activity_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='internal_notes',
            field=openrepairplatform.fields.CleanHTMLField(blank=True, verbose_name="Notes de l'évènement visibles en interne"),
        ),
        migrations.AddField(
            model_name='historicalevent',
            name='internal_notes',
            field=openrepairplatform.fields.CleanHTMLField(blank=True, verbose_name="Notes de l'évènement visibles en interne"),
        ),
    ]
