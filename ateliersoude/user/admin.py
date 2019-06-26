from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import CustomUser, Organization, Membership
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser


class MembershipResource(resources.ModelResource):
    class Meta:
        model = Membership


class OrganizationResource(resources.ModelResource):
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


class MembershipAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = MembershipResource


class OrganizationAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    resource_class = OrganizationResource


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Membership, MembershipAdmin)
