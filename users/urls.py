from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.UserListView.as_view(), name='user_list'),
    url(r'^userprofile/', views.user_profile, name='user_profile'),
    url(r'^(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user_detail'),
     
]
