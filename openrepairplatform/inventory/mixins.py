from openrepairplatform.inventory.models import ThermalPrinter

class PermissionEditUserStuffMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            if self.object.member_owner == user:
                context["can_edit"] = True
            else:
                if self.object.organization_owner:
                    if self.object.organization_owner in user.get_active_or_more_organizations():
                        context["can_edit"] = True

                elif self.object.member_owner:
                    for organization in self.object.member_owner.get_organizations():
                        if organization in user.get_active_or_more_organizations():
                            context["can_edit"] = True
        return context


class PermissionCreateUserStuffMixin:

    ## nota : ce mixin est aussi utilsé pour créer une cotisation sur la page du membre, ce qui ne va pas puisque ce n'est pas un stuff mais une fee. 
    # Ce n'est pas dramatique mais à patcher
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        if self.request.user.is_authenticated:
            if user == self.request.user:
                context["can_create"] = True
                context["same_user"] = True
            else:
                user_organizations = user.get_organizations()
                for organization in user_organizations:
                    if organization in self.request.user.get_active_or_more_organizations():
                        context["can_create"] = True
        return context


class ThermalPrintersContextMixin:
    def add_thermal_printers(self, context, *, organization=None, member_user=None):
        editable_organizations = []
        user = self.request.user

        if not user.is_authenticated:
            context["thermal_printers_active"] = []
            context["can_print"] = False
            return context

        if organization:
            if organization in user.get_active_or_more_organizations():
                editable_organizations.append(organization)

        elif member_user:
            for orga in member_user.get_organizations():
                if orga in user.get_active_or_more_organizations():
                    editable_organizations.append(orga)

        printers = ThermalPrinter.objects.filter(active=True, organization__in=editable_organizations)

        context["thermal_printers_active"] = list(printers)
        context["can_print"] = printers.exists()
        return context

