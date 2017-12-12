from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
    # url(r'^$', views.UserListView.as_view(), name='user_list'),
    url(r'^organization/$', views.OrganizationListView.as_view(), name='organization_list'),
    url(r'^organization/create/$', views.OrganizationCreateView.as_view(), name='organization_create'),
    url(r'^organization/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.OrganizationView.as_view(), name='organization_detail'),
    url(r'^organization/(?P<pk>[0-9]+)/edit/$', views.OrganizationEditView.as_view(), name='organization_edit'),
    url(r'^place/$', views.PlaceListView.as_view(), name='place_list'),
    url(r'^place/create/$', views.PlaceCreateView.as_view(), name='place_create'),
    url(r'^place/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.PlaceView.as_view(), name='place_detail'),
    url(r'^place/(?P<pk>[0-9]+)/edit/$', views.PlaceEditView.as_view(), name='place_edit'),
    url(r'^event/$', views.EventListView.as_view(), name='event_list'),
    url(r'^event/create/$', views.EventCreateView.as_view(), name='event_create'),
    url(r'^event/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.EventView.as_view(), name='event_detail'),
    url(r'^event/(?P<pk>[0-9]+)/edit/$', views.EventEditView.as_view(), name='event_edit'),
]
