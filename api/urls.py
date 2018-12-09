from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^deleteEvent/$', views.delete_event, name='delete_event'),
    url(r'^setPresent/$', views.set_present, name='set_present'),
    url(r'^setAbsent/$', views.set_absent, name='set_absent'),
    url(r'^getOrganizations/$', views.get_organizations, name='get_organizations'),
    url(r'^getPlacesForOrganization/$', views.get_places_for_organization, name='get_places_for_organization'),
    url(r'^getPlaces/$', views.get_all_places, name='get_all_places'),
    url(r'^getDates/$', views.get_dates, name='get_dates'),
    url(r'^getUsers/(?P<organization_pk>[0-9]+)/(?P<event_pk>[0-9]+)/$', views.list_users, name='list_users'),
    url(r'^addUsers/$', views.add_users, name='add_users'),
    url(r'^list_events/$', views.list_events_in_context, name='list_events_in_context'),
    url(r'^list_events_user/(?P<context_type>[-\w]+)/(?P<context_pk>[0-9]+)/$', views.list_events_in_context, {'context_user':'yes'}, name='list_events_user'),
    url(r'^list_events_place/(?P<context_type>[-\w]+)/(?P<context_pk>[0-9]+)/$', views.list_events_in_context, {'context_place':'yes'}, name='list_events_place'),
    url(r'^list_events_organization/(?P<context_type>[-\w]+)/(?P<context_pk>[0-9]+)/$', views.list_events_in_context, {'context_org':'yes'}, name='list_events_organization'),
    url(r'^book/$', views.book_event, name='book'),
]
