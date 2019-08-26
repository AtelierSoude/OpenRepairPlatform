from django.urls import path

from . import views

app_name = "inventory"
urlpatterns = [
    path(
        "<int:stuff_pk>/",
        views.StuffDetailView.as_view(),
        name="stuff_view"
    ),
    path(
        "create_stuff/",
        views.StuffCreateView.as_view(),
        name="create_stuff"
    ),
    path(
        "update_stuff/<int:stuff_pk>/",
        views.StuffUpdateView.as_view(),
        name="update_stuff"
    ),
]
