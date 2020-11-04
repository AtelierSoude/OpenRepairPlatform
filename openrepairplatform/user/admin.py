from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.fields import Field

from .models import CustomUser, Organization, Membership, Fee
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser


class FeeResource(resources.ModelResource):
    class Meta:
        model = Fee


class MembershipResource(resources.ModelResource):
    user = Field(
        column_name="user",
        attribute="user",
        widget=ForeignKeyWidget(CustomUser, "id")
    )
    organization = Field(
        column_name="organization",
        attribute="organization",
        widget=ForeignKeyWidget(Organization, "id")
    )

    class Meta:
        model = Membership


class OrganizationResource(resources.ModelResource):
    members = Field(
        column_name="members",
        attribute="members",
        widget=ManyToManyWidget(CustomUser)
    )
    volunteers = Field(
        column_name="volunteers",
        attribute="volunteers",
        widget=ManyToManyWidget(CustomUser)
    )
    visitors = Field(
        column_name="visitors",
        attribute="visitors",
        widget=ManyToManyWidget(CustomUser)
    )
    actives = Field(
        column_name="actives",
        attribute="actives",
        widget=ManyToManyWidget(CustomUser)
    )
    admins = Field(
        column_name="admins",
        attribute="admins",
        widget=ManyToManyWidget(CustomUser)
    )

    class Meta:
        model = Organization


class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = CustomUserResource
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "street_address",
                    "birth_date",
                    "bio",
                    "is_visible",
                    "avatar_img",
                )
            },
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ('first_name', 'last_name', 'email')


class FeeAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = FeeResource


class MembershipAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = MembershipResource


class OrganizationAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = OrganizationResource


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Fee, FeeAdmin)

