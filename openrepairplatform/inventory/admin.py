from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from import_export.admin import ImportExportActionModelAdmin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .models import (
    Stuff,
    Device,
    Brand,
    Category,
    Observation,
    Action,
    Reasoning,
    Intervention,
    RepairFolder,
    Status,
)


class DeviceAdmin(DynamicArrayMixin, SimpleHistoryAdmin):
    class Meta:
        model = Device


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category


class CategoryAdmin(ImportExportActionModelAdmin, TreeAdmin):
    form = movenodeform_factory(Category)


admin.site.register(Brand, SimpleHistoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Stuff, SimpleHistoryAdmin)
admin.site.register(Observation, SimpleHistoryAdmin)
admin.site.register(Action, SimpleHistoryAdmin)
admin.site.register(Reasoning, SimpleHistoryAdmin)
admin.site.register(Intervention, SimpleHistoryAdmin)
admin.site.register(RepairFolder, SimpleHistoryAdmin)
admin.site.register(Status, SimpleHistoryAdmin)
