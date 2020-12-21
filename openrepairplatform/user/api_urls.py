from django.urls import path
from rest_framework import routers

from . import api_views
app_name = "api_user"

router = routers.SimpleRouter()
router.register(r'', api_views.CustomUserViewSet)
urlpatterns = router.urls