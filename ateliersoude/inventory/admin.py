from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Stuff, Device, Brand, Category, SubCategory


admin.site.register(Brand, SimpleHistoryAdmin)
admin.site.register(Category, SimpleHistoryAdmin)
admin.site.register(SubCategory, SimpleHistoryAdmin)
admin.site.register(Device, SimpleHistoryAdmin)
admin.site.register(Stuff, SimpleHistoryAdmin)
