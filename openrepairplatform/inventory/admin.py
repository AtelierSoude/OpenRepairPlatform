from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Stuff, Device, Brand, Category, Observation, Action, Reasoning, DiagnosisOrRepairStep, RepairFolder, Status

class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)

admin.site.register(Brand, SimpleHistoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Device, SimpleHistoryAdmin)
admin.site.register(Stuff, SimpleHistoryAdmin)
admin.site.register(Observation, SimpleHistoryAdmin)
admin.site.register(Action, SimpleHistoryAdmin)
admin.site.register(Reasoning, SimpleHistoryAdmin)
admin.site.register(DiagnosisOrRepairStep, SimpleHistoryAdmin)
admin.site.register(RepairFolder, SimpleHistoryAdmin)
admin.site.register(Status, SimpleHistoryAdmin)



