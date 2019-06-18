from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from ateliersoude.location.models import Place

admin.site.register(Place, SimpleHistoryAdmin)
