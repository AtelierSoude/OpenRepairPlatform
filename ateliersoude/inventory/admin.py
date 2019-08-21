from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Stuff


admin.site.register(Stuff, SimpleHistoryAdmin)
