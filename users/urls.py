from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^userprofile/', views.user_profile, name='user_profile'),
    url(r'^$', views.user_profile, name='user_profile'),
]
