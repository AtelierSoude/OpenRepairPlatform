from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Activity, Condition, Event, Participation
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.fields import Field


class ActivityResource(resources.ModelResource):
    class Meta:
        model = Activity


class EventResource(resources.ModelResource):
    activity = Field(
        column_name="activity",
        attribute="activity",
        widget=ForeignKeyWidget("Activity", "id")
    )
    organization = Field(
        column_name="organization",
        attribute="organization",
        widget=ForeignKeyWidget("Organization", "id")
    )
    registered = Field(
        column_name="registered",
        attribute="registered",
        widget=ManyToManyWidget("CustomUser")
    )
    presents = Field(
        column_name="presents",
        attribute="presents",
        widget=ManyToManyWidget("CustomUser")
    )

    class Meta:
        model = Event


class ParticipationResource(resources.ModelResource):
    user = Field(
        column_name="user",
        attribute="user",
        widget=ForeignKeyWidget("CustomUser", "id")
    )
    event = Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget("Event", "id")
    )

    class Meta:
        model = Participation


class ActivityAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = ActivityResource


class EventAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = EventResource


class ParticipationAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = ParticipationResource


admin.site.register(Event, EventAdmin)
admin.site.register(Condition, SimpleHistoryAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Participation, ParticipationAdmin)
