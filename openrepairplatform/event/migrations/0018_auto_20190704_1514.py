# Generated by Django 2.2 on 2019-07-04 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0017_auto_20190704_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalevent',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
    ]
