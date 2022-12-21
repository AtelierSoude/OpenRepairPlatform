# Generated by Django 3.2.2 on 2021-05-21 15:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0034_auto_20201220_1713'),
        ('user', '0026_auto_20210517_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalmembership',
            name='fee',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='fee',
        ),
        migrations.AddField(
            model_name='fee',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fees', to='event.event'),
        ),
        migrations.AddField(
            model_name='historicalorganization',
            name='membership_url',
            field=models.URLField(blank=True, default='', max_length=255, verbose_name="Lien d'adhésion en ligne"),
        ),
        migrations.AddField(
            model_name='organization',
            name='membership_url',
            field=models.URLField(blank=True, default='', max_length=255, verbose_name="Lien d'adhésion en ligne"),
        ),
        migrations.AlterField(
            model_name='fee',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fees', to='user.membership', verbose_name='Liée à une adhésion'),
        ),
        migrations.AlterField(
            model_name='historicalmembership',
            name='first_payment',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='historicalorganization',
            name='membership_system',
            field=models.CharField(choices=[('date_year', "L'adhésion dure un an à partir de la date de la première contribution."), ('date_month', "L'adhésion dure un mois à partir de la date de la première contribution."), ('year', "L'adhésion est pour l'année en cours et se renouvelle à chaque début d'année."), ('month', "L'adhésion est mensuelle, elle se renouvelle chaque début de mois.")], default='date_year', max_length=10),
        ),
        migrations.AlterField(
            model_name='membership',
            name='first_payment',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='organization',
            name='membership_system',
            field=models.CharField(choices=[('date_year', "L'adhésion dure un an à partir de la date de la première contribution."), ('date_month', "L'adhésion dure un mois à partir de la date de la première contribution."), ('year', "L'adhésion est pour l'année en cours et se renouvelle à chaque début d'année."), ('month', "L'adhésion est mensuelle, elle se renouvelle chaque début de mois.")], default='date_year', max_length=10),
        ),
    ]