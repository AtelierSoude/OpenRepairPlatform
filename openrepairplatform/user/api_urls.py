from . import api_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = "api_user"

router = DefaultRouter()
router.register(r'webhooks', api_views.WebHookViewSet, basename='webhook')

urlpatterns = [
    path("<int:pk>/", api_views.CustomUserAPIView.as_view(), name="detail"),
    path("webhook/<uuid:webhook_pk>/", api_views.MembershipWebhookView.as_view({'post': 'create'}), name="membership_webhook"),

    # Routes WebHook via DRF Router sous le préfixe dynamique orga_slug
    path("<str:orga_slug>/", include(router.urls)),
]
