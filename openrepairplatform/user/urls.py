from django.urls import path

from . import views
from openrepairplatform.mixins import (
    CreateMembershipMixin,
    UpdateMembershipMixin,
    DeleteMembershipMixin,
)

app_name = "user"
urlpatterns = [
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("update/<int:pk>", views.UserUpdateView.as_view(), name="user_update"),
    path("create/", views.UserCreateView.as_view(), name="user_create"),
    path(
        "create_and_book/",
        views.UserCreateAndBookView.as_view(),
        name="create_and_book",
    ),
    path(
        "organizer_book/<int:pk>/",
        views.OrganizerBookView.as_view(),
        name="organizer_book",
    ),
    path(
        "organizations/",
        views.OrganizationListView.as_view(),
        name="organization_list",
    ),
    path(
        "organization/create/",
        views.OrganizationCreateView.as_view(),
        name="organization_create",
    ),
    path(
        "organization/<int:pk>/update/",
        views.OrganizationUpdateView.as_view(),
        name="organization_update",
    ),
    path(
        "organization/<int:orga_pk>/<slug>/events/<int:page>/",
        views.OrganizationEventsListView.as_view(),
        name="organization_all_events",
    ),
    path(
        "organization/<int:pk>/",
        views.OrganizationDeleteView.as_view(),
        name="organization_delete",
    ),
    path(
        "organization/<int:pk>/add-admin",
        views.AddAdminToOrganization.as_view(),
        name="organization_add_admin",
    ),
    path(
        "organization/<int:pk>/add-active",
        views.AddActiveToOrganization.as_view(),
        name="organization_add_active",
    ),
    path(
        "organization/<int:pk>/add-volunteer",
        views.AddVolunteerToOrganization.as_view(),
        name="organization_add_volunteer",
    ),
    path(
        "organization/<int:pk>/<int:user_pk>/remove-from-actives",
        views.RemoveActiveFromOrganization.as_view(),
        name="remove_from_actives",
    ),
    path(
        "organization/<int:pk>/<int:user_pk>/remove-from-volunteers",
        views.RemoveVolunteerFromOrganization.as_view(),
        name="remove_from_volunteers",
    ),
    path(
        "organization/<int:pk>/<int:user_pk>/remove-from-admins",
        views.RemoveAdminFromOrganization.as_view(),
        name="remove_from_admins",
    ),
    path(
        "organization/<int:pk>/add-member",
        CreateMembershipMixin.as_view(),
        name="organization_add_member",
    ),
    path(
        "organization/<int:orga_pk>/update-member/<int:pk>",
        UpdateMembershipMixin.as_view(),
        name="organization_update_member",
    ),
    path(
        "delete-member/<int:pk>", DeleteMembershipMixin.as_view(), name="delete_member"
    ),
    path(
        "fee/<int:pk>/delete/",
        views.FeeDeleteView.as_view(),
        name="fee_delete",
    ),
]
