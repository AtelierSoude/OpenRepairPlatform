from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^setPresent/$', views.set_present, name='set_present'),
]
