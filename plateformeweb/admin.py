from django.contrib import admin
from .models import Event, EventType, Place, Organization, OrganizationPerson


class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type', 'published', 'starts_at', 'available_seats',
        'location', 'slug')
    ordering = ('-starts_at',)

class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'raw_address', 'slug')

    def raw_address(self, obj):
        return obj.address.raw

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'active')


admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationPerson)
