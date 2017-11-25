"""skinjay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^plateformeweb/', include('plateformeweb.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/settings/', include('dbsettings.urls')),
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('users.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^avatar/', include('avatar.urls')),
]

# DEBUG toolbar if DEBUG is true in the environment (see ../skinjay/settings.py)
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

# https://stackoverflow.com/questions/4938491/django-admin-change-header-django-administration-text

admin.site.site_header = 'Atelier Soudé'
admin.site.index_title = 'Administration'
admin.site.site_title = 'Atelier Soudé Admin'
