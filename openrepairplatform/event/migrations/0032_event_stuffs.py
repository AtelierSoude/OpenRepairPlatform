# Generated by Django 2.2.4 on 2020-12-04 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0020_auto_20201204_1128'),
        ('event', '0031_auto_20201114_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='stuffs',
            field=models.ManyToManyField(related_name='events', to='inventory.Stuff'),
        ),
    ]
