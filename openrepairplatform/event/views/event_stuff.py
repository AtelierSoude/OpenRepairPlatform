from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, View

from openrepairplatform.event.models import Event
from openrepairplatform.inventory.views import StuffFormMixin
from openrepairplatform.inventory.models import Stuff
from openrepairplatform.user.models import CustomUser


class EventBookStuffView(TemplateView):
    template_name = "event/book_confirm_add_stuff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = Event.objects.get(pk=self.kwargs["pk"])
        context["event_menu"] = "active"
        context["registered_user"] = CustomUser.objects.get(pk=self.kwargs["user_pk"])
        return context


class StuffUserEventFormView(StuffFormMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["visitor_user"] = CustomUser.objects.get(pk=self.kwargs["registered_pk"])
        kwargs["event"] = Event.objects.get(pk=self.kwargs["event_pk"])
        return kwargs

    def get_success_url(self, *args, **kwargs):
        event = Event.objects.get(pk=self.kwargs["event_pk"])
        registered_pk = self.kwargs["registered_pk"]
        next_url = reverse("event:detail", args=[event.id, event.slug])
        next_url = f"{next_url}?success_booking=True&user_pk={registered_pk}"
        return next_url


class StuffUserOrgaEventFormView(StuffFormMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["visitor_user"] = CustomUser.objects.get(pk=self.kwargs["registered_pk"])
        kwargs["event"] = Event.objects.get(pk=self.kwargs["event_pk"])
        return kwargs

    def form_valid(self, form):
        res = super().form_valid(form)
        stuff = form.instance
        event = Event.objects.get(pk=self.kwargs["event_pk"])
        if stuff:
            event.stuffs.add(stuff)
            event.save()
        return res


    def form_valid(self, form):
        res = super().form_valid(form)
        stuff = form.instance 
        import pdb; pdb.set_trace()
        
        messages.success(self.request, f"l'objet #{stuff.pk} bien ajouté à l'inventaire")
        return res


    def get_success_url(self, *args, **kwargs):
        event = Event.objects.get(pk=self.kwargs["event_pk"])
        registered_pk = self.kwargs["registered_pk"]
        return reverse("event:detail_admin", args=[event.id, event.slug])


class EventAddStuffView(View):
    model = Event
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        stuff_pk = self.request.POST.get("selectedstuff")
        stuff = Stuff.objects.get(pk=stuff_pk)
        event = Event.objects.get(pk=kwargs["pk"])
        event.stuffs.add(stuff)
        event.save()
        return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        event = Event.objects.get(pk=self.kwargs["pk"])
        messages.success(
            self.request,
            "L'objet a bien été ajouté à votre réservation !",
        )
        return reverse("event:detail", args=[event.id, event.slug])
