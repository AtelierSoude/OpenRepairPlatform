import django_tables2 as tables
from openrepairplatform.user.models import Fee, CustomUser
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
        return super(MemberTable, self).get_column_default_show()

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
            "full_name",
            "membership_status",
            "member_update",
        ]
        return super(MemberTable, self).get_column_default_show()

    full_name = tables.Column(accessor="full_name", verbose_name="Nom", linkify=True)
    email = tables.Column(linkify=False)
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
        model = CustomUser
        attrs = {"class": "table table-fixed table-hover"}
        sequence = (
            "avatar",
            "full_name",
            "email",
            "street_address",
            "phone_number",
            "membership_status",
            "member_update",
        )
        exclude = (
            "password",
            "last_name",
            "id",
            "is_active",
            "is_visible",
            "is_superuser",
            "last_login",
            "date_joined",
            "birth_date",
            "bio",
            "is_staff",
            "gender",
            "avatar_img",
            "first_name",
        )


class FeeTable(tables.Table):
    user = tables.Column(linkify=True, verbose_name="Membre")
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
        sequence = ("date", "user", "participation", "payment", "amount")
        exclude = ("organization", "id")
