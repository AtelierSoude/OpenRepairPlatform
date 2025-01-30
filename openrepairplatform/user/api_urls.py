from . import api_views
from django.urls import path

app_name = "api_user"

urlpatterns = [
    path("<int:pk>/", api_views.CustomUserAPIView.as_view(), name="detail")
]
