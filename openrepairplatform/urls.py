from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

from . import views
from ateliersoude.inventory.views import OrganizationStockView


urlpatterns = [
    path("", views.HomeView.as_view(), name="homepage"),
    path("user/", include("openrepairplatform.user.urls", namespace="user")),
    path("avatar/", include('initial_avatars.urls')),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("event/", include("openrepairplatform.event.urls", namespace="event")),
    path(
        "inventory/",
        include("ateliersoude.inventory.urls", namespace="inventory")
    ),
    path(
        "location/",
        include("openrepairplatform.location.urls", namespace="location"),
    ),
    path(
        "api/location/",
        include("openrepairplatform.location.api_urls", namespace="api_location"),
    ),
    path(
        "api/user/",
        include("ateliersoude.user.api_urls", namespace="api_user"),
    ),
    path(
        "place_autocomplete/", 
        views.PlaceAutocomplete.as_view(), 
        name="place_autocomplete",
    ),
    path(
        "activity_autocomplete/", 
        views.ActivityAutocomplete.as_view(), 
        name="activity_autocomplete",
    ),
    path(
        "user_autocomplete/",
        views.CustomUserAutocomplete.as_view(), 
        name="user_autocomplete",
    ),
    path(
        "<str:orga_slug>/user_orga_autocomplete/",
        views.ActiveOrgaAutocomplete.as_view(), 
        name="user_orga_autocomplete",
    ),
    path(
        "<str:orga_slug>/",
        views.OrganizationPageView.as_view(),
        name="organization_page",
    ),
    path(
        "<str:orga_slug>/groups/",
        views.OrganizationGroupsView.as_view(),
        name="organization_groups",
    ),
    path(
        "<str:orga_slug>/members/",
        views.OrganizationMembersView.as_view(),
        name="organization_members",
    ),
    path(
        "<str:orga_slug>/details/",
        views.OrganizationDetailsView.as_view(),
        name="organization_details"
    ),
    path(
        "<str:orga_slug>/controls/",
        views.OrganizationControlsView.as_view(),
        name="organization_controls"
    ),
    path(
        "<str:orga_slug>/events/",
        views.OrganizationEventsView.as_view(),
        name="organization_events"
    ),
    path(
        "<str:orga_slug>/stock/",
        OrganizationStockView.as_view(),
        name="organization_stock"
    ),
    path(
        "<str:orga_slug>/accounting/",
        views.OrganizationFeesView.as_view(),
        name="organization_fees"
    ),
    path(r"tinymce/", include("tinymce.urls")),
]

if settings.DEBUG:
    import debug_toolbar  # noqa

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
