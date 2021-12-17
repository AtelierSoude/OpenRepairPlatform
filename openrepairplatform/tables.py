import django_tables2 as tables
from openrepairplatform.user.models import Fee, CustomUser, Membership
from openrepairplatform.event.models import Event
from django_tables2_column_shifter.tables import ColumnShiftTable


class EventTable(ColumnShiftTable):
    def get_column_default_show(self):
        self.column_default_show = [
            "date",
            "activity",
            "location",
            "needed_organizers",
            "seats",
            "action",
        ]
        return super(EventTable, self).get_column_default_show()

    date = tables.TemplateColumn(
        accessor="date",
        template_name="extra_column_data.html",
        verbose_name="Date",
        extra_context={"column": "date"},
    )
    location = tables.Column(attrs={"td": {"class": "small"}})
    needed_organizers = tables.TemplateColumn(
        accessor="needed_organizers",
        template_name="extra_column_data.html",
        verbose_name="Animateurs",
        extra_context={"column": "needed_organizers"},
    )
    seats = tables.TemplateColumn(
        accessor="available_seats",
        template_name="extra_column_data.html",
        extra_context={"column": "seats"},
        verbose_name="Places",
    )
    action = tables.TemplateColumn(
        accessor="get_absolute_url",
        template_name="extra_column_data.html",
        extra_context={"column": "details"},
        verbose_name="Action",
        linkify=True,
    )

    class Meta:
        model = Event
        attrs = {"class": "table table-fixed table-hover"}
        sequence = (
            "date",
            "activity",
            "location",
            "collaborator",
            "needed_organizers",
            "seats",
            "published",
            "action",
        )
        exclude = (
            "id",
            "organization",
            "starts_at",
            "ends_at",
            "description",
            "external",
            "external_url",
            "slug",
            "is_free",
            "booking",
            "created_at",
            "updated_at",
            "available_seats",
            "publish_at",
        )


class MemberTable(ColumnShiftTable):
    def get_column_default_show(self):
        self.column_default_show = [
            "avatar",
            "user",
            "membership_status",
            "member_update",
        ]
        return super(MemberTable, self).get_column_default_show()

    user = tables.Column(linkify=True, verbose_name="Membre")
    email = tables.Column(accessor="user.email")
    street_address = tables.Column(accessor="user.street_address")
    avatar = tables.TemplateColumn(
        template_name="extra_column_data.html",
        extra_context={"column": "avatar"},
        verbose_name="",
        attrs={"td": {"class": "small-column"}, "th": {"class": "small-column"}},
    )
    membership_status = tables.TemplateColumn(
        template_name="extra_column_data.html",
        extra_context={"column": "membership_status"},
        verbose_name="Statut",
        attrs={"td": {"class": "text-right"}, "th": {"class": "text-right"}},
    )
    member_update = tables.TemplateColumn(
        template_name="extra_column_data.html",
        extra_context={"column": "member_update"},
        verbose_name="Action",
    )

    class Meta:
        model = Membership
        attrs = {"class": "table table-fixed table-hover"}
        sequence = (
            "avatar",
            "user",
            "email",
            "street_address",
            "membership_status",
            "disabled",
            "member_update",
        )
        exclude = (
            "first_payment",
            "organization",
            "amount",
            "id"
        )


class FeeTable(tables.Table):
    membership = tables.Column(linkify=True, verbose_name="Membre")
    participation = tables.RelatedLinkColumn(
        verbose_name="Evénement", attrs={"td": {"class": "small"}}
    )
    payment = tables.Column(
        verbose_name="Paiement",
    )
    amount = tables.Column(
        verbose_name="Montant", attrs={"td": {"class": "font-weight-bold"}}
    )

    class Meta:
        model = Fee
        attrs = {"class": "table table-fixed table-hover"}
        sequence = ("date", "membership", "participation", "payment", "amount")
        exclude = ("organization", "id")
