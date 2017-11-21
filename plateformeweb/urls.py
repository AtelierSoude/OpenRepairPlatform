from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name="homepage"),
    url(r'^userprofile/', views.user_profile, name='user_profile'),
]
