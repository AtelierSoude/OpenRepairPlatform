import django_tables2 as tables
from ateliersoude.user.models import (
    Fee
)


class FeeTable(tables.Table):
    user = tables.Column(
        linkify=True, 
        verbose_name="Membre"
        )
    participation = tables.RelatedLinkColumn(
        verbose_name="Evénement", 
        attrs={"td": {"class": "small"}}
        )
    payment = tables.Column(
        verbose_name="Paiement", 
        )
    amount = tables.Column(
        verbose_name="Montant",
     attrs={"td": {"class": "font-weight-bold"}}
        )

    class Meta:
        model = Fee
        sequence = ('date', 'user', 'participation', 'payment', 'amount')
        exclude = ("organization", 'id' )
