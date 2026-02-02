from dal import autocomplete
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Q, F, Max, Sum
from django.utils.safestring import mark_safe
from django.db.models import Case, When, Value, IntegerField


from django.contrib.staticfiles import finders
from bootstrap_modal_forms.generic import (
    BSModalCreateView,
    BSModalUpdateView,
)
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.generic import (
    UpdateView,
    DetailView,
)
from openrepairplatform.mixins import HasActivePermissionMixin
from openrepairplatform.user.mixins import PermissionOrgaContextMixin
from openrepairplatform.inventory.mixins import PermissionEditStuffMixin, DeviceContextAutocompleteMixin
from openrepairplatform.inventory.mixins import PermissionCreateUserStuffMixin, PermissionEditUserStuffMixin, ThermalPrintersContextMixin

import django_tables2 as tables
from django_filters.views import FilterView
from django_tables2.export.views import ExportMixin

from .tables import StockTable
from .models import (
    Stuff,
    Action,
    Device,
    Category,
    Observation,
    Status,
    Reasoning,
    Brand,
    Intervention,
    RepairFolder, ThermalPrinter,
)
from .filters import StockFilter
from .forms import (
    StuffForm,
    FolderForm,
    StuffEditOwnerForm,
    StuffVisibilityForm,
    StuffEditPlaceForm,
    StuffEditStateForm,
    InterventionForm,
    StuffUpdateForm,
)
from openrepairplatform.user.models import CustomUser, Organization


class StockListView(FilterView):
    model = Stuff
    filterset_class = StockFilter
    template_name = "inventory/stock_list.html"

    def get_queryset(self):
        queryset = Stuff.objects.filter(is_visible=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stock_menu"] = "active"
        return context


class DeviceDetailView(DetailView):
    model = Device
    template_name = "inventory/device_detail.html"


def StuffUserListView(self, *args, **kwargs):
    data = dict()
    if self.method == "GET":
        user = CustomUser.objects.get(pk=kwargs["user_pk"])
        stuffs = user.user_stuffs
        # asyncSettings.dataKey = 'table'
        data["html_stuffs_list"] = render_to_string(
            "inventory/user_stuffs_table.html", {"stuffs": stuffs}, request=self
        )
        return JsonResponse(data)


class OrganizationStockView(
    HasActivePermissionMixin,
    PermissionOrgaContextMixin,
    ExportMixin,
    tables.SingleTableMixin,
    FilterView,
):
    model = Stuff
    template_name = "organization_stock.html"
    context_object_name = "stock"
    paginate_by = 30
    table_class = StockTable
    filterset_class = StockFilter
    dataset_kwargs = {"title": "Stock"}

    def get_queryset(self):
        self.object = self.organization
        return Stuff.objects.filter(organization_owner=self.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["stock_tab"] = "active"
        context["organization_menu"] = "active"
        return context


class StuffDetailView(PermissionEditUserStuffMixin, ThermalPrintersContextMixin, DetailView):
    model = Stuff
    template_name = "inventory/stuff_detail.html"
    pk_url_kwarg = "stuff_pk"

    def get_context_data(self, *args, **kwargs):
        context_stuff = super().get_context_data(*args, **kwargs)
        self.add_thermal_printers(
            context_stuff, 
            organization=self.object.organization_owner, 
            member_user=self.object.member_owner)
        return context_stuff

class StuffFormMixin(BSModalCreateView, PermissionCreateUserStuffMixin, ThermalPrintersContextMixin):
    model = Stuff
    form_class = StuffForm
    template_name = "inventory/stuff_form.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        form_kwargs = self.get_form_kwargs()
        orga = form_kwargs.get("organization")
        member_user = form_kwargs.get("user")
        if form_kwargs.get("visitor_user"):
            orga = form_kwargs.get('event').organization
        self.add_thermal_printers(context, organization=orga, member_user=member_user)
        return context

    def form_valid(self, form):
        res = super().form_valid(form)
        stuff = form.instance 
        if self.request.POST.get("submit_action") == "create_print":
            print_thermal_label(self.request, stuff.pk)
        messages.success(self.request, f"l'objet #{stuff.pk} bien ajouté à l'inventaire")
        return res



class StuffUserFormView(StuffFormMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = CustomUser.objects.get(pk=self.kwargs["user_pk"])
        return kwargs

    def get_success_url(self, *args, **kwargs):
        user = CustomUser.objects.get(pk=self.kwargs["user_pk"])
        return user.get_absolute_url()


class StuffOrganizationFormView(StuffFormMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = Organization.objects.get(slug=self.kwargs["orga_slug"])
        return kwargs

    def get_success_url(self, *args, **kwargs):
        return reverse(
            "organization_stock",
            kwargs={"orga_slug": self.kwargs["orga_slug"]},
        )


class StuffUpdateViewMixin(BSModalUpdateView):
    model = Stuff
    form_class = StuffForm
    template_name = "inventory/stuff_edit_form.html"
    success_message = "L'objet a bien été modifié"

    def form_valid(self, form):
        res = super().form_valid(form)
        return res

    def get_success_url(self, *args, **kwargs):
        stuff = Stuff.objects.get(pk=self.kwargs["pk"])
        return stuff.get_absolute_url()


class StuffUpdateView(StuffUpdateViewMixin, UpdateView):
    form_class = StuffUpdateForm
    template_name = "inventory/stuff_edit_form.html"
    success_message = "L'objet a bien été modifié"


class StuffEditVisibilityStuffView(StuffUpdateViewMixin, UpdateView):
    form_class = StuffVisibilityForm
    template_name = "inventory/stuff_edit_visibility_form.html"
    success_message = "La visibilité a bien été modifié"


class StuffUpdateOwnerView(StuffUpdateViewMixin, UpdateView):
    form_class = StuffEditOwnerForm
    template_name = "inventory/stuff_edit_owner_form.html"
    success_message = "Le propriétaire a bien été modifié"


class StuffUpdatePlaceView(StuffUpdateViewMixin, UpdateView):
    form_class = StuffEditPlaceForm
    template_name = "inventory/stuff_edit_place_form.html"
    success_message = "La localisation a bien été modifiée"


class StuffUpdateStateView(StuffUpdateViewMixin, UpdateView):
    model = Stuff
    form_class = StuffEditStateForm
    template_name = "inventory/stuff_edit_state_form.html"
    success_message = "L'état a bien été modifié"


class FolderCreateView(BSModalCreateView):
    model = RepairFolder
    template_name = "inventory/folder_create_form.html"
    form_class = FolderForm
    success_message = "Le dossier a bien été créé"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["stuff"] = Stuff.objects.get(pk=self.kwargs["pk"])
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        stuff = Stuff.objects.get(pk=self.kwargs["pk"])
        return stuff.get_absolute_url()


class InterventionCreateView(BSModalCreateView):
    model = Intervention
    template_name = "inventory/intervention_create_form.html"
    form_class = InterventionForm
    success_message = "L'intervention a bien été créé"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["folder"] = RepairFolder.objects.get(pk=self.kwargs["pk"])
        kwargs["stuff"] = kwargs["folder"].stuff
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        folder = RepairFolder.objects.get(pk=self.kwargs["pk"])
        stuff = folder.stuff
        return stuff.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["folder"] = RepairFolder.objects.get(pk=self.kwargs["pk"])
        return context


class InterventionUpdateView(BSModalUpdateView):
    model = Intervention
    template_name = "inventory/intervention_create_form.html"
    form_class = InterventionForm
    success_message = "L'intervention a bien été modifiée"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        intervention = Intervention.objects.get(pk=self.kwargs["pk"])
        kwargs["folder"] = intervention.folder
        kwargs["event"] = intervention.event
        kwargs["stuff"] = kwargs["folder"].stuff
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        intervention = Intervention.objects.get(pk=self.kwargs["pk"])
        stuff = intervention.folder.stuff
        return stuff.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intervention = Intervention.objects.get(pk=self.kwargs["pk"])
        context["folder"] = intervention.folder
        context["update_intervention"] = intervention
        return context


# views for autocompletion
class DeviceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Device.objects.all()
        category_pk = self.forwarded.get("category", None)

        if category_pk:
            category = Category.objects.get(pk=category_pk)
            qs = Device.objects.filter(category=category)
            childrens = category.get_children()
            descendants = category.get_descendants()
            if childrens:
                for children in childrens:
                    qsadd = Device.objects.filter(category=children)
                qs = qs.union(qsadd)
                if descendants:
                    for descendant in descendants:
                        qsadd = Device.objects.filter(category=descendant)
                    qs = qs.union(qsadd)

        if self.q:
            qs = qs.filter(slug__icontains=self.q)
        return qs


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        if item.get_parent():
            return f"{item.get_parent()} > {item}"
        else:
            return f"{item}"

    def get_queryset(self):
        qs = Category.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class BrandAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Brand.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True

#### ci dessous , customisation des queryset pour Observation, Action, Reasoning afin d'afficher 
#### en priorité les résultats (pondérés) les plus probables suivant le précédent champ renseigné, le a catégorie et la catégorie parente
#### et afficher un pourcentage.

### C'est pas très beau mais tout ceci sera à revoir au passage sur vuejs et l'abandon d'autocomplete

class ObservationAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self, *args, **kwargs):
        device_id = self.request.GET.get("device")

        base = Observation.objects.all()
        category = None
        parent_category = None

        if device_id:
            try:
                device = Device.objects.select_related("category").get(pk=device_id)
                category = device.category
            except Device.DoesNotExist:
                category = None

            if category:
                try:
                    parent_category = category.get_parent()
                except AttributeError:
                    parent_category = None

        if not category and not parent_category:
            qs = base.annotate(
                usage_count=Count("intervention", distinct=True)
            )

            self.score_attr = "usage_count"
            self.total_score = (
                qs.aggregate(
                    total_score=Sum("usage_count", filter=Q(usage_count__gt=0))
                )["total_score"]
                or 0
            )

            if self.q:
                qs = qs.annotate(
                    match_rank=Case(
                        When(name__istartswith=self.q, then=Value(2)),
                        When(name__icontains=self.q, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
            else:
                qs = qs.annotate(match_rank=Value(0, output_field=IntegerField()))

            return qs.order_by("-match_rank", "-usage_count", "name")

        direct_filter = Q()
        parent_filter = Q()

        if category:
            direct_filter |= Q(intervention__folder__stuff__device__category_id=category.id)
            direct_filter |= Q(intervention__folder__stuff__device_id=device_id)

        if parent_category:
            parent_filter |= Q(intervention__folder__stuff__device__category_id=parent_category.id)

        qs = base.annotate(
            direct_count=Count("intervention", filter=direct_filter, distinct=True),
            parent_count=Count("intervention", filter=parent_filter, distinct=True),
        ).annotate(
            score=3 * F("direct_count") + 1 * F("parent_count")
        )

        self.score_attr = "score"
        self.total_score = (
            qs.aggregate(
                total_score=Sum("score", filter=Q(score__gt=0))
            )["total_score"]
            or 0
        )

        if self.q:
            qs = qs.annotate(
                match_rank=Case(
                    When(name__istartswith=self.q, then=Value(2)),
                    When(name__icontains=self.q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        else:
            qs = qs.annotate(match_rank=Value(0, output_field=IntegerField()))

        return qs.order_by("-match_rank", "-score", "name")

    def get_result_label(self, result):
        score_attr = getattr(self, "score_attr", None)
        total_score = getattr(self, "total_score", 0) or 0

        raw = getattr(result, score_attr, 0) if score_attr else 0
        if total_score > 0 and raw > 0:
            percent = int(round(raw * 100 / total_score))
        else:
            percent = 0

        return mark_safe(
            f"{result.name}"
            f"<span class='badge rounded-pill bg-light float-end'>{percent}%</span>"
        )

    def has_add_permission(self, request):
        return True

class ActionAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self, *args, **kwargs):
        device_id = self.request.GET.get("device")

        forwarded = getattr(self, "forwarded", {})
        reasoning_id = forwarded.get("reasoning") or self.request.GET.get("reasoning")

        base = Action.objects.all()
        category = None
        parent_category = None

        if device_id:
            try:
                device = Device.objects.select_related("category").get(pk=device_id)
                category = device.category
            except Device.DoesNotExist:
                category = None

            if category:
                try:
                    parent_category = category.get_parent()
                except AttributeError:
                    parent_category = None

        if not category and not parent_category:
            qs = base.annotate(
                effective_count=Count("intervention", distinct=True),
            )

            self.total_effective = (
                qs.aggregate(
                    total=Sum("effective_count", filter=Q(effective_count__gt=0))
                )["total"]
                or 0
            )

            if self.q:
                qs = qs.annotate(
                    match_rank=Case(
                        When(name__istartswith=self.q, then=Value(2)),
                        When(name__icontains=self.q, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
            else:
                qs = qs.annotate(match_rank=Value(0, output_field=IntegerField()))

            return qs.order_by("-match_rank", "-effective_count", "name")

        child_filter = Q()
        parent_filter = Q()

        if category:
            child_filter &= Q(intervention__folder__stuff__device__category_id=category.id)
        if parent_category:
            parent_filter &= Q(intervention__folder__stuff__device__category_id=parent_category.id)

        if reasoning_id:
            child_filter &= Q(intervention__reasoning_id=reasoning_id)
            parent_filter &= Q(intervention__reasoning_id=reasoning_id)

        qs = base.annotate(
            child_count=Count("intervention", filter=child_filter, distinct=True),
            parent_count=Count("intervention", filter=parent_filter, distinct=True),
        ).annotate(
            effective_count=F("child_count") + F("parent_count")
        )

        agg = qs.aggregate(
            total_child=Sum("child_count", filter=Q(child_count__gt=0)),
            total_parent=Sum("parent_count", filter=Q(parent_count__gt=0)),
        )
        self.total_effective = (agg["total_child"] or 0) + (agg["total_parent"] or 0)

        if self.q:
            qs = qs.annotate(
                match_rank=Case(
                    When(name__istartswith=self.q, then=Value(2)),
                    When(name__icontains=self.q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        else:
            qs = qs.annotate(match_rank=Value(0, output_field=IntegerField()))

        return qs.order_by("-match_rank", "-effective_count", "-child_count", "name")

    def get_result_label(self, result):
        child = getattr(result, "child_count", 0) or 0
        parent = getattr(result, "parent_count", 0) or 0
        eff = child + parent

        total = getattr(self, "total_effective", 0) or 0
        if total > 0 and eff > 0:
            percent = int(round(eff * 100 / total))
        else:
            percent = 0

        return mark_safe(
            f"{result.name}"
            f"<span class='badge rounded-pill bg-light float-end'>{percent}%</span>"
        )

    def has_add_permission(self, request):
        return True

class ReasoningAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self, *args, **kwargs):
        device_id = self.request.GET.get("device")

        forwarded = getattr(self, "forwarded", {})
        observation_id = forwarded.get("observation") or self.request.GET.get("observation")

        base = Reasoning.objects.all()
        category = None
        parent_category = None

        if device_id:
            try:
                device = Device.objects.select_related("category").get(pk=device_id)
                category = device.category
            except Device.DoesNotExist:
                category = None

            if category:
                try:
                    parent_category = category.get_parent()
                except AttributeError:
                    parent_category = None

        if not category and not parent_category:
            qs = base.annotate(
                effective_count=Count("intervention", distinct=True),
            )

            self.total_effective = (
                qs.aggregate(
                    total=Sum("effective_count", filter=Q(effective_count__gt=0))
                )["total"]
                or 0
            )

            if self.q:
                qs = qs.annotate(
                    match_rank=Case(
                        When(name__istartswith=self.q, then=Value(2)),
                        When(name__icontains=self.q, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
            else:
                qs = qs.annotate(match_rank=Value(0, output_field=IntegerField()))

            return qs.order_by("-match_rank", "-effective_count", "name")

        child_filter = Q()
        parent_filter = Q()

        if category:
            child_filter &= Q(intervention__folder__stuff__device__category_id=category.id)
        if parent_category:
            parent_filter &= Q(intervention__folder__stuff__device__category_id=parent_category.id)

        if observation_id:
            child_filter &= Q(intervention__observation_id=observation_id)
            parent_filter &= Q(intervention__observation_id=observation_id)

        qs = base.annotate(
            child_count=Count("intervention", filter=child_filter, distinct=True),
            parent_count=Count("intervention", filter=parent_filter, distinct=True),
        ).annotate(
            effective_count=F("child_count") + F("parent_count")
        )

        agg = qs.aggregate(
            total_child=Sum("child_count", filter=Q(child_count__gt=0)),
            total_parent=Sum("parent_count", filter=Q(parent_count__gt=0)),
        )
        self.total_effective = (agg["total_child"] or 0) + (agg["total_parent"] or 0)

        if self.q:
            qs = qs.annotate(
                match_rank=Case(
                    When(name__istartswith=self.q, then=Value(2)),
                    When(name__icontains=self.q, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        else:
            qs = qs.annotate(match_rank=Value(0, output_field=IntegerField()))

        return qs.order_by("-match_rank", "-effective_count", "-child_count", "name")

    def get_result_label(self, result):
        child = getattr(result, "child_count", 0) or 0
        parent = getattr(result, "parent_count", 0) or 0
        eff = child + parent

        total = getattr(self, "total_effective", 0) or 0
        if total > 0 and eff > 0:
            percent = int(round(eff * 100 / total))
        else:
            percent = 0

        return mark_safe(
            f"{result.name}"
            f"<span class='badge rounded-pill bg-light float-end'>{percent}%</span>"
        )

    def has_add_permission(self, request):
        return True

class StatusAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Status.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

    def has_add_permission(self, request):
        return True


### PRINTER
### BETA VERSION - ONLY TESTED WITH TP35 

def print_thermal_label(request, pk, *args, **kwargs):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    stuff = get_object_or_404(Stuff, pk=pk)
    thermal_printer = get_object_or_404(ThermalPrinter, pk=request.POST.get('printer_pk'))
    data_printed = {"timeout" : 2}
    if thermal_printer:
        data_printed["host"] = thermal_printer.ip
        if thermal_printer.port :
            data_printed['port'] = thermal_printer.port
        if thermal_printer.profile :
            data_printed['profile'] = thermal_printer.profile

        # on importe la lib ici pour éviter de surcharger le controleur
        from escpos.printer import Network
        import qrcode
        from PIL import Image, ImageDraw, ImageFont
        import os

        print(data_printed)
        try :
            printer = Network(**data_printed)
            if printer.is_online():

                WIDTH = 262 
                HEIGHT = 90

                img = Image.new("RGB", (WIDTH, HEIGHT), "white")
                draw = ImageDraw.Draw(img)
                w, h = img.size
                draw.rectangle((0, 0, w-1, h-1), outline="black", width=1)

                # Logo
                logo_path = finders.find("img/logo_thermal-print.png")        
                if logo_path:
                    logo = Image.open(logo_path)
                    logo.thumbnail((140, 80))
                    img.paste(logo, (77, 0), logo)

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    border=1,
                )
                qr.add_data(stuff.get_url_qrcode())
                qr.make()
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_img.thumbnail((70, 70))
                img.paste(qr_img, (10, 10))
                site = os.environ.get("DOMAINDNS")
                font_big = ImageFont.truetype("../usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16 )
                font_small = ImageFont.truetype("../usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10 )
                draw.text((80, 38), "ID/", font=font_big, fill="black")
                draw.text((110, 38), f"{stuff.pk}", font=font_big, fill="black")
                draw.text((80, 57), "retrouve et modifie mon carnet", font=font_small, fill="black")
                draw.text((80, 67), "de santé sur " + f"{site}" , font=font_small, fill="black")

                printer.image(img, impl="bitImageRaster", center=False)
                printer.cut()
                printer.close()
                
        except Exception as e:
            print(f"printer error {e} : {data_printed}")

    return redirect(request.META.get('HTTP_REFERER') or reverse("home"))
