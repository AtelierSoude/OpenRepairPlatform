from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
    # url(r'^$', views.UserListView.as_view(), name='user_list'),
    url(r'^organization/$', views.OrganizationListView.as_view(), name='organization_list'),
    url(r'^organization/create/$', views.OrganizationCreateView.as_view(), name='organization_create'),
    url(r'^organization/(?P<pk>[0-9]+)/edit/$', views.OrganizationEditView.as_view(), name='organization_edit'),
    url(r'^organization/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.OrganizationView.as_view(), name='organization_detail'),
    url(r'^organization_manager/(?P<pk>[0-9]+)/$', views.OrganizationManager, name='organization_manager'),
    url(r'^place/$', views.PlaceListView.as_view(), name='place_list'),
    url(r'^place/create/$', views.PlaceCreateView.as_view(), name='place_create'),
    url(r'^place/(?P<pk>[0-9]+)/edit/$', views.PlaceEditView.as_view(), name='place_edit'),
    url(r'^place/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.PlaceView.as_view(), name='place_detail'),
    url(r'^condition/create/$', views.ConditionCreateView.as_view(), name='condition_create'),
    url(r'^condition/(?P<pk>[0-9]+)/edit/$', views.ConditionEditView.as_view(), name='condition_edit'),
    url(r'^activity/$', views.ActivityListView.as_view(), name='activity_list'),
    url(r'^activity/create/$', views.ActivityCreateView.as_view(), name='activity_create'),
    url(r'^activity/(?P<pk>[0-9]+)/edit/$', views.ActivityEditView.as_view(), name='activity_edit'),
    url(r'^activity/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.ActivityView.as_view(), name='activity_detail'),
    url(r'^event/$', views.EventListView.as_view(), name='event_list'),
    url(r'^event/create/$', views.EventCreateView.as_view(), name='event_create'),
    url(r'^event/cancel_reservation/(?P<token>.+)/', views.cancel_reservation, name='cancel_reservation'),
    url(r'^event/(?P<pk>[0-9]+)/book/$', views.BookingEditView.as_view(), name='booking_form'),
    url(r'^event/(?P<pk>[0-9]+)/edit/$', views.EventEditView.as_view(), name='event_edit'),
    url(r'^event/(?P<pk>[0-9]+)/(?P<slug>[-\w]+)/$', views.EventView.as_view(), name='event_detail'),
    url(r'^massevent/book/$', views.MassBookingCreateView.as_view(), name='mass_event_book'),
]
