from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from ateliersoude.location.models import Place


class PlaceResource(resources.ModelResource):
    class Meta:
        model = Place


class PlaceAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = PlaceResource


admin.site.register(Place, PlaceAdmin)
