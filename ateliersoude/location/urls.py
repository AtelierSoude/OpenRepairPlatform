from django.urls import path

from . import views

app_name = "location"
urlpatterns = [
    path("", views.PlaceMapView.as_view(), name="list"),
    path(
        "create/<int:orga_pk>", views.PlaceCreateView.as_view(), name="create"
    ),
    path("<int:pk>/edit/", views.PlaceEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.PlaceDeleteView.as_view(), name="delete"),
    path("<int:pk>/<slug>/", views.PlaceView.as_view(), name="detail"),
]
