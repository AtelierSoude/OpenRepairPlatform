from django.urls import path

from .api_views import EventCreateAPIView, EventUpdateAPIView

app_name = "api_event"
urlpatterns = [
    path("", EventCreateAPIView.as_view(), name="create-event"),
    path("<int:pk>/", EventUpdateAPIView.as_view(), name="update-event"),
]
