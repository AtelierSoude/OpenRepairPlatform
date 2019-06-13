from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Activity, Condition, Event, Participation

admin.site.register(Event, SimpleHistoryAdmin)
admin.site.register(Condition, SimpleHistoryAdmin)
admin.site.register(Activity, SimpleHistoryAdmin)
admin.site.register(Participation, SimpleHistoryAdmin)
