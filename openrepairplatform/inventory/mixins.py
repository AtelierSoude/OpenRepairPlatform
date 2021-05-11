class PermissionEditStuffMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            if self.object.member_owner == user:
                context["can_edit"] = user
            else:
                if self.object.organization_owner:
                    organization = self.object.organization_owner
                    context["can_edit"] = user in (
                        organization.actives.all().union(
                            organization.volunteers.all(), organization.admins.all()
                        )
                    )
                elif self.object.member_owner:
                    owner_organizations = user.member_organizations.all().union(
                        user.member_organizations.all(),
                        user.visitor_organizations.all(),
                        user.volunteer_organizations.all(),
                        user.active_organizations.all(),
                        user.admin_organizations.all(),
                    )
                    for organization in owner_organizations:
                        if user in (
                            organization.actives.all().union(
                                organization.volunteers.all(), organization.admins.all()
                            )
                        ):
                            can_edit = True
                    if can_edit:
                        context["can_edit"] = True
        return context


class PermissionCreateUserStuffMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        can_create = False
        if self.request.user.is_authenticated:
            if user == self.request.user:
                context["can_create"] = user
            else:
                user_organizations = user.member_organizations.all().union(
                    user.member_organizations.all(),
                    user.visitor_organizations.all(),
                    user.volunteer_organizations.all(),
                    user.active_organizations.all(),
                    user.admin_organizations.all(),
                )
                for organization in user_organizations:
                    if self.request.user in (
                        organization.actives.all().union(
                            organization.volunteers.all(), organization.admins.all()
                        )
                    ):
                        can_create = True
                if can_create is True:
                    context["can_create"] = True
        return context
