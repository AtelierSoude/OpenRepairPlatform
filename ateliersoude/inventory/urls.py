from django.urls import path
from django.conf.urls import url
from . import views

app_name = "inventory"
urlpatterns = [
    path(
        "<int:stuff_pk>/",
        views.StuffDetailView.as_view(),
        name="stuff_view"
    ),
    path(
        "create_stuff/<str:orga_slug>/",
        views.StuffOrganizationCreateView.as_view(),
        name="create_organization_stuff"
    ),
    path(
        "create_stuff/<int:user_pk>/",
        views.StuffUserCreateView.as_view(),
        name="create_user_stuff"
    ),
    path(
        "update_stuff/<int:stuff_pk>/",
        views.StuffUpdateView.as_view(),
        name="update_stuff"
    ),
]
