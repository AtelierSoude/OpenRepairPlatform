from django.views.generic import ListView
from ateliersoude.mixins import HasActivePermissionMixin
from ateliersoude.user.mixins import PermissionOrgaContextMixin

from .models import Stuff


class OrganizationStockView(
    HasActivePermissionMixin, PermissionOrgaContextMixin, ListView
        ):
    model = Stuff
    template_name = "organization_stock.html"
    context_object_name = "stock"
    paginate_by = 50

    def get_queryset(self):
        self.object = self.organization
        return Stuff.objects.filter(organization_owner=self.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        return context
