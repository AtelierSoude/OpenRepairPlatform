from django.urls import path
from django.conf.urls import url
from . import views

app_name = "inventory"
urlpatterns = [
    path(
        "device/<int:pk>/<slug>/",
        views.DeviceDetailView.as_view(),
        name="device_view"
    ),
    path(
        "<int:stuff_pk>/",
        views.StuffDetailView.as_view(),
        name="stuff_view"
    ),
      path(
        "create_stuff/<int:user_pk>/",
        views.StuffCreateView.as_view(),
        name="create_user_stuff"
    ),
    path(
        "create_stuff/<str:orga_slug>/",
        views.StuffOrganizationCreateView.as_view(),
        name="create_organization_stuff"
    ),
    path(
        "update_stuff/<int:stuff_pk>/",
        views.StuffUpdateView.as_view(),
        name="update_stuff"
    ),
]