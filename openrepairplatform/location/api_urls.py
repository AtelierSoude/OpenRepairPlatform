from django.urls import path

from . import api_views

app_name = "api_location"
urlpatterns = [path("place-list/", api_views.PlaceListAPIView.as_view(), name="places")]
