from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from import_export.fields import Field

from openrepairplatform.location.models import Place
from openrepairplatform.user.models import Organization


class PlaceResource(resources.ModelResource):
    organization = Field(
        column_name="organization",
        attribute="organization",
        widget=ForeignKeyWidget(Organization, "id")
    )

    class Meta:
        model = Place


class PlaceAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = PlaceResource


admin.site.register(Place, PlaceAdmin)
