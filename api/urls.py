from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^setPresent/$', views.set_present, name='set_present'),
    url(r'^setAbsent/$', views.set_absent, name='set_absent'),
    url(r'^getOrganizations/$', views.get_organizations, name='get_organizations'),
    url(r'^getDates/$', views.get_dates, name='get_dates'),
    url(r'^list_events/$', views.list_events, name='list_events'),
    url(r'^book/$', views.book, name='book'),
]
