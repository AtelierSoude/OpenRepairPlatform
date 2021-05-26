from django.urls import path

from . import views
from openrepairplatform.mixins import CreateMembershipMixin, UpdateMembershipMixin

app_name = "event"


urlpatterns = [
    path(
        "future_event_place_autocomplete/",
        views.FutureEventPlaceAutocomplete.as_view(),
        name="future_event_place_autocomplete",
    ),
    path(
        "future_event_activity_autocomplete/",
        views.FutureEventActivityAutocomplete.as_view(),
        name="future_event_activity_autocomplete",
    ),
    path(
        "<str:orga_slug>/condition_orga_autocomplete/",
        views.ConditionOrgaAutocomplete.as_view(),
        name="condition_orga_autocomplete",
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
    path("create/<int:orga_pk>/", views.EventCreateView.as_view(), name="create"),
    path(
        "recurrent/create/<int:orga_pk>/",
        views.RecurrentEventCreateView.as_view(),
        name="recurrent_create",
    ),
    path("<int:pk>/edit/", views.EventEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
    # path("<int:pk>/close/", views.CloseEventView.as_view(), name="close"),
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
    # path("<int:pk>/close/", views.CloseEventView.as_view(), name="close"),
    path("<int:pk>/<slug>/", views.EventView.as_view(), name="detail"),
    path(
        "<int:pk>/<slug>/book/<int:user_pk>/<token>",
        views.EventBookStuffView.as_view(),
        name="book_confirm",
    ),
    path(
        "<int:pk>/add_stuff/<int:user_pk>",
        views.EventAddStuffView.as_view(),
        name="add_stuff_event",
    ),
    path(
        "create_stuff/<int:event_pk>/<int:registered_pk>/<token>",
        views.StuffUserEventFormView.as_view(),
        name="create_user_event_stuff",
    ),
    path(
        "cancel_reservation/<token>/",
        views.CancelReservationView.as_view(),
        name="cancel_reservation",
    ),
    path("book/<token>/", views.BookView.as_view(), name="book"),
    path("absent/<token>/", views.AbsentView.as_view(), name="user_absent"),
    path("present/<token>/", views.PresentView.as_view(), name="user_present"),
    path(
        "add-to-member/<int:pk>/<int:event_pk>/",
        CreateMembershipMixin.as_view(),
        name="add_member",
    ),
    path(
        "update-member/<int:orga_pk>/<int:pk>/<int:event_pk>/",
        UpdateMembershipMixin.as_view(),
        name="update_member",
    ),
    path(
        "add-participation/<int:user_pk>/<int:event_pk>/",
        views.ParticipationCreateView.as_view(),
        name="add_participation",
    ),
    path(
        "update-participation/<int:pk>/",
        views.ParticipationUpdateView.as_view(),
        name="update_participation",
    ),
    path(
        "delete-participation/<int:pk>/",
        views.ParticipationDeleteView.as_view(),
        name="delete_participation",
    ),
]
