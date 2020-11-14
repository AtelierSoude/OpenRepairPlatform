class PermissionOrgaContextMixin:
    """
    Adds some context variables: telling us which information the current user
    can see in templates
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, "organization"):
            organization = self.object.organization
        else:
            organization = self.object
        user = self.request.user
        context["is_admin"] = user in organization.admins.all()
        context["is_active"] = (
            user in organization.actives.all() or context["is_admin"]
        )
        context["is_volunteer"] = (
            user in organization.volunteers.all() or context["is_active"]
        )
        return context
