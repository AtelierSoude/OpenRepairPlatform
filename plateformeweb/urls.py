from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
    # url(r'^$', views.UserListView.as_view(), name='user_list'),
    url(r'^organization/$', views.OrganizationListView.as_view(), name='organization_list'),
    url(r'^organization/create/$', views.OrganizationCreateView.as_view(), name='organization_create'),
    url(r'^organization/(?P<pk>[-\w]+)/$', views.OrganizationView.as_view(), name='organization_detail'),
    url(r'^organization/(?P<pk>[-\w]+)/edit/$', views.OrganizationEditView.as_view(), name='organization_edit'),
]
