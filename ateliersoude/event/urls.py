from django.urls import path
from django.conf.urls import url

from . import views

app_name = "event"


urlpatterns = [
    url(
        r'place_autocomplete/$', 
        views.PlaceAutocomplete.as_view(), 
        name="place_autocomplete",
    ),
    path(
        "condition/create/<int:orga_pk>/",
        views.ConditionCreateView.as_view(),
        name="condition_create",
    ),
    path(
        "condition/<int:pk>/edit/",
        views.ConditionEditView.as_view(),
        name="condition_edit",
    ),
    path(
        "condition/<int:pk>/delete/",
        views.ConditionDeleteView.as_view(),
        name="condition_delete",
    ),
    path("activity/", views.ActivityListView.as_view(), name="activity_list"),
    path(
        "activity/create/<int:orga_pk>/",
        views.ActivityCreateView.as_view(),
        name="activity_create",
    ),
    path(
        "activity/<int:pk>/edit/",
        views.ActivityEditView.as_view(),
        name="activity_edit",
    ),
    path(
        "activity/<int:pk>/delete/",
        views.ActivityDeleteView.as_view(),
        name="activity_delete",
    ),
    path(
        "activity/<int:pk>/<slug>/",
        views.ActivityView.as_view(),
        name="activity_detail",
    ),
    path("", views.EventListView.as_view(), name="list"),
    path(
        "create/<int:orga_pk>/", views.EventCreateView.as_view(), name="create"
    ),
    path(
        "recurrent/create/<int:orga_pk>/",
        views.RecurrentEventCreateView.as_view(),
        name="recurrent_create",
    ),
    path("<int:pk>/edit/", views.EventEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
    path("<int:pk>/close/", views.CloseEventView.as_view(), name="close"),
    path(
        "<int:pk>/add_active/",
        views.AddActiveEventView.as_view(),
        name="add_active",
    ),
    path(
        "<int:pk>/remove_active/",
        views.RemoveActiveEventView.as_view(),
        name="remove_active",
    ),
    path("<int:pk>/close/", views.CloseEventView.as_view(), name="close"),
    path("<int:pk>/<slug>/", views.EventView.as_view(), name="detail"),
    path(
        "cancel_reservation/<token>/",
        views.CancelReservationView.as_view(),
        name="cancel_reservation",
    ),
    path("book/<token>/", views.BookView.as_view(), name="book"),
    path("absent/<token>/", views.AbsentView.as_view(), name="user_absent"),
]
