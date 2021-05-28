import logging
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import RedirectView
from django.shortcuts import get_object_or_404

from openrepairplatform import utils
from openrepairplatform.mail import event_send_mail
from openrepairplatform.event.models import Event
from openrepairplatform.mixins import HasVolunteerPermissionMixin, _load_token


logger = logging.getLogger(__name__)


class BookView(RedirectView):

    def is_authorized(self, event):
        if self.request.user.is_anonymous:
            return False
        return self.request.user in event.organization.actives.all().union(
            event.organization.volunteers.all(),
            event.organization.admins.all(),
        )

    def send_mail(self, event, user):
        date = event.date.strftime("%d %B")
        subject = (
            f"Votre réservation du {date} pour {event.activity.name}"
            f" à {event.location.name}"
        )
        event_send_mail(
            event,
            user,
            subject,
            "event/mail/book.txt",
            "event/mail/book.html",
            f"{event.organization} <{settings.DEFAULT_FROM_EMAIL}>",
            [user.email],
            request=self.request,
        )

    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "book")
        except Exception:
            logger.exception(f"Error loading token {token} during book")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        is_authorized = self.is_authorized(event)

        next_url = self.request.GET.get("redirect")
        if not utils.is_valid_path(next_url):
            if user:
                user_pk = user.pk
            else:
                user_pk = self.request.user.pk
            if is_authorized:
                next_url = reverse(
                    "event:detail", args=[event.id, event.slug]
                )
                next_url = f"{next_url}?success_booking=True&user_pk={user_pk}"
            else:
                next_url = reverse(
                    "event:detail", args=[event.id, event.slug]
                )
                next_url = f"{next_url}?success_booking=True&user_pk={user_pk}"

        if event.remaining_seats <= 0 and not is_authorized:
            messages.error(
                self.request,
                "Désolé, il n'y a plus de place " "disponibles pour cet évènement",
            )
            next_url = reverse("event:detail", args=[event.id, event.slug])
            return next_url

        if user in event.presents.all().union(event.registered.all()):
            messages.success(
                self.request,
                "Vous êtes déjà inscrit à cet évènement, à bientôt !",
            )
            next_url = reverse("event:detail", args=[event.id, event.slug])
            return next_url

        event.registered.add(user)

        self.send_mail(event, user)

        messages.success(self.request, f"'{user}' bien inscrit à l'évènement !")

        return next_url


class AddActiveEventView(HasVolunteerPermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        event.organizers.add(self.request.user)
        messages.success(self.request, "Ajouté aux animateurs !")

        return reverse("event:detail", args=[event.id, event.slug])


class RemoveActiveEventView(HasVolunteerPermissionMixin, RedirectView):
    http_method_names = ["post"]
    model = Event

    def get_redirect_url(self, *args, **kwargs):
        event_pk = kwargs["pk"]
        event = get_object_or_404(Event, pk=event_pk)
        event.organizers.remove(self.request.user)
        messages.success(self.request, "Retiré des animateurs !")

        return reverse("event:detail", args=[event.id, event.slug])


class CancelReservationView(RedirectView):

    def send_mail(self, event, user):
        date = event.date.strftime("%d %B")
        subject = (
            f"Confirmation d'annulation pour le " f"{date} à {event.location.name}"
        )
        event_send_mail(
            event,
            user,
            subject,
            "event/mail/unbook.txt",
            "event/mail/unbook.html",
            f"{event.organization} <{settings.DEFAULT_FROM_EMAIL}>",
            [user.email],
            request=self.request,
        )

    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        try:
            event, user = _load_token(token, "cancel")
        except Exception:
            logger.exception(f"Error loading token {token} during unbook")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")
        if event.allow_stuffs:
            user_stuffs = event.stuffs.all().filter(member_owner=user)
            if user_stuffs:
                for stuff in user_stuffs:
                    event.stuffs.remove(stuff)

        event.registered.remove(user)
        event.presents.remove(user)

        if user.first_name == "":
            # This is a temporary user created only for this event, we can
            # delete it
            user.delete()

        self.send_mail(event, user)

        messages.success(
            self.request,
            f"{user} n'est plus inscrit·e à cet événement."
        )

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class PresentView(RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            self.event, self.user = _load_token(kwargs["token"], "present")
        except Exception:
            messages.error(request, "Le lien est pas autorisé.")
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        res = super().get(request, *args, **kwargs)
        self.event.presents.add(self.user)
        return res

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "event:detail", kwargs={"pk": self.event.pk, "slug": self.event.slug}
        )


class AbsentView(RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            self.event, self.user = _load_token(kwargs["token"], "absent")
        except Exception:
            messages.error(request, "Le lien est pas autorisé.")
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        res = super().get(request, *args, **kwargs)
        self.event.presents.remove(self.user)
        return res

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "event:detail", kwargs={"pk": self.event.pk, "slug": self.event.slug}
        )
