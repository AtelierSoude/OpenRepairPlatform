from django.urls import reverse
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

class DeviceContextAutocompleteMixin:
    """
    - Déduit un device_id OU une category_id depuis le form
      (stuff, instance, category passé en __init__, initial…)
    - Ajoute ?device=… et/ou ?category=… aux URLs des widgets
      observation / reasoning / action / status.
    - Pour InterventionForm, on peut aussi pré-remplir observation / reasoning.
    """

    AUTOCOMPLETE_FIELDS = ["observation", "reasoning", "action", "status"]

    def _guess_device_id(self):
        # 1. stuff passé au form (InterventionForm, FolderForm, etc.)
        stuff = getattr(self, "stuff", None)
        if stuff and getattr(stuff, "device_id", None):
            return stuff.device_id

        # 2. instance Intervention : folder -> stuff -> device
        instance = getattr(self, "instance", None)
        if instance and getattr(instance, "pk", None) and hasattr(instance, "folder"):
            folder = instance.folder
            if folder and folder.stuff and folder.stuff.device_id:
                return folder.stuff.device_id

        # 3. instance Stuff : device direct (StuffUpdateForm, etc.)
        if instance and hasattr(instance, "device_id") and instance.device_id:
            return instance.device_id

        # 4. initial["device"] sur un ModelChoiceField
        initial_device = getattr(self, "initial", {}).get("device")
        if initial_device:
            # peut être un pk ou une instance
            return getattr(initial_device, "pk", initial_device)

        return None

    def _guess_category_id(self):
        """
        Permet d'avoir au moins une catégorie même si le Stuff n'est pas encore créé.
        Utile pour StuffForm en création.
        """
        # 1. category passée explicitement en __init__
        category = getattr(self, "category", None)
        if category:
            return getattr(category, "pk", category)

        # 2. si on a un stuff avec device → on peut en déduire category
        stuff = getattr(self, "stuff", None)
        if stuff and getattr(stuff, "device", None) and stuff.device.category_id:
            return stuff.device.category_id

        # 3. instance avec device → category via instance.device
        instance = getattr(self, "instance", None)
        if instance and hasattr(instance, "device") and instance.device and instance.device.category_id:
            return instance.device.category_id

        # 4. initial["category"] (StuffForm en création)
        initial_category = getattr(self, "initial", {}).get("category")
        if initial_category:
            return getattr(initial_category, "pk", initial_category)

        return None

    def _guess_observation_id(self):
        instance = getattr(self, "instance", None)
        if instance and getattr(instance, "pk", None) and hasattr(instance, "observation_id"):
            return instance.observation_id or None
        return None

    def _guess_reasoning_id(self):
        instance = getattr(self, "instance", None)
        if instance and getattr(instance, "pk", None) and hasattr(instance, "reasoning_id"):
            return instance.reasoning_id or None
        return None

    def set_autocomplete_urls(self):
        device_id = self._guess_device_id()
        category_id = self._guess_category_id()
        obs_id = self._guess_observation_id()
        reasoning_id = self._guess_reasoning_id()

        for field_name in self.AUTOCOMPLETE_FIELDS:
            if field_name not in self.fields:
                continue
            widget = self.fields[field_name].widget
            if not hasattr(widget, "url"):
                continue

            base_url = widget.url
            params = []

            if device_id:
                params.append(f"device={device_id}")
            elif category_id:
                # si pas de device mais une catégorie → on envoie au moins la catégorie
                params.append(f"category={category_id}")

            # pour ReasoningAutocomplete, on pré-remplit observation
            if field_name == "reasoning" and obs_id:
                params.append(f"observation={obs_id}")

            # pour ActionAutocomplete, on pré-remplit reasoning
            if field_name == "action" and reasoning_id:
                params.append(f"reasoning={reasoning_id}")

            if params:
                sep = "&" if "?" in base_url else "?"
                widget.url = f"{base_url}{sep}{'&'.join(params)}"
            else:
                widget.url = base_url
