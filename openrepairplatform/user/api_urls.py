from . import api_views
from django.urls import path

app_name = "api_user"

urlpatterns = [
    path("<int:pk>/", api_views.CustomUserAPIView.as_view(), name="detail"),
    path("webhook/<uuid:webhook_pk>/", api_views.MembershipWebhookView.as_view({'post': 'create'}), name="membership_webhook"),


    # Routes pour la gestion des WebHooks par organisation
    # Les actions list et create sont regroupées sur l'URL de base
    path(
        "<str:orga_slug>/webhooks/", 
        api_views.WebHookViewSet.as_view({'get': 'list', 'post': 'create'}), 
        name="webhook-list"
    ),
    # L'action delete (destroy) utilise l'UUID du webhook
    path(
        "<str:orga_slug>/webhooks/<uuid:pk>/", 
        api_views.WebHookViewSet.as_view({'delete': 'destroy'}), 
        name="webhook-detail"
    ),
]
