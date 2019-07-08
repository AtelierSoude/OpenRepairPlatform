from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="homepage"),
    path("user/", include("ateliersoude.user.urls", namespace="user")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("event/", include("ateliersoude.event.urls", namespace="event")),
    path(
        "location/",
        include("ateliersoude.location.urls", namespace="location"),
    ),
    path(
        "api/location/",
        include("ateliersoude.location.api_urls", namespace="api_location"),
    ),
    path(
        "<slug>/",
        views.OrganizationDetailView.as_view(),
        name="organization_detail",
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
