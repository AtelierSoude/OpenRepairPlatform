# Generated by Django 3.2.2 on 2021-05-26 13:11

from django.db import migrations


def presents_user_is_registered(app, schema_editor):
    Event = app.get_model("event", "Event")
    for event in Event.objects.all():
        for user in event.presents.all():
            event.registered.add(user)


class Migration(migrations.Migration):


    dependencies = [
        ('event', '0037_auto_20210525_1352'),
    ]

    operations = [
        migrations.RunPython(
            presents_user_is_registered , migrations.RunPython.noop
        )
    ]
