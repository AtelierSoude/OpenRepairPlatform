from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _
from simple_history.admin import SimpleHistoryAdmin

from .models import CustomUser, Organization, Membership
from .forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin):
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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, SimpleHistoryAdmin)
admin.site.register(Membership, SimpleHistoryAdmin)
