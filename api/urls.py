from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^deleteEvent/$', views.delete_event, name='delete_event'),
    url(r'^setPresent/$', views.set_present, name='set_present'),
    url(r'^setAbsent/$', views.set_absent, name='set_absent'),
    url(r'^getOrganizations/$', views.get_organizations, name='get_organizations'),
    url(r'^getPlacesForOrganization/$', views.get_places_for_organization, name='get_places_for_organization'),
    url(r'^getDates/$', views.get_dates, name='get_dates'),
    url(r'^list_events/$', views.list_events, name='list_events'),
    url(r'^book/$', views.book_event, name='book'),
]
