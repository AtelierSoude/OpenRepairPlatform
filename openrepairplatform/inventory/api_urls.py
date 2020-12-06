from django.urls import path
from rest_framework import routers

from . import api_views
app_name = "api_inventory"

router = routers.SimpleRouter()
router.register(r'stuff', api_views.StuffViewSet)
router.register(r"stuff/(?P<stuff_pk>\d+)/folder", api_views.RepairFolderViewSet)
router.register(r"intervention", api_views.InterventionViewSet)
router.register(r'device', api_views.DeviceViewSet)

urlpatterns = router.urls