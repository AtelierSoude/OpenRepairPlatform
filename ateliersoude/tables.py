import django_tables2 as tables
from ateliersoude.user.models import (
    Fee, CustomUser
)

class MemberTable(tables.Table):

    full_name = tables.Column(
        accessor='full_name', 
        verbose_name='Nom',
        linkify=True
        )
    email = tables.Column(linkify=False)
    avatar = tables.TemplateColumn(
        template_name="extra_column_data.html",
        extra_context={"column": "avatar"},
        verbose_name="",
        attrs={"td": {"class": "small-column"},"th": {"class": "small-column"}}
        )
    membership_status = tables.TemplateColumn(
        template_name="extra_column_data.html",
        extra_context={"column": "membership_status"},
        verbose_name="Statut",
        attrs={"td": {"class": "text-right"},"th": {"class": "text-right"}}
        )
    member_update = tables.TemplateColumn(
        template_name="extra_column_data.html",
        extra_context={"column": "member_update"},
        verbose_name="Action"
        )

    class Meta:
        model = CustomUser
        attrs = {"class": "table table-fixed"}
        sequence = ('avatar', 'full_name', 'email', 'membership_status', 'member_update')
        exclude = (
            "password", 
            'last_name',
            'id', 
            'is_active',
            'is_visible',
            'is_superuser', 
            'last_login', 
            'date_joined', 
            'birth_date', 
            'bio', 
            'is_staff',
            'gender',
            'avatar_img',
            'phone_number',
            'first_name',
            'street_address',
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
        attrs = {"class": "table table-fixed"}
        sequence = ('date', 'user', 'participation', 'payment', 'amount')
        exclude = ("organization", 'id' )
