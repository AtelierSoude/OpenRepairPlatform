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
    def add_thermal_printers(self, context, stuff):
        editable_organizations = []
        if stuff.organization_owner:
            if stuff.organization_owner in self.request.user.get_active_or_more_organizations():
                editable_organizations.append(stuff.organization_owner)
        elif stuff.member_owner:
            for organization in stuff.member_owner.get_organizations():
                if organization in self.request.user.get_active_or_more_organizations():
                    editable_organizations.append(organization)
        printers = ThermalPrinter.objects.filter(active=True, organization__in=editable_organizations)
        if printers.exists():
            context["thermal_printers_active"] = list(printers)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stuff = getattr(self, "object", None)  
        if stuff:
            return self.add_thermal_printers(context, stuff)
        return context
