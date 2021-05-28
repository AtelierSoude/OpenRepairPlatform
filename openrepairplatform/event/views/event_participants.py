import logging
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import RedirectView
from django.shortcuts import get_object_or_404

from openrepairplatform import utils
from openrepairplatform.event.models import Event
from openrepairplatform.event.templatetags.app_filters import tokenize
from openrepairplatform.mixins import HasVolunteerPermissionMixin, _load_token
from openrepairplatform.user.models import CustomUser


logger = logging.getLogger(__name__)


class BookView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        token = kwargs["token"]
        is_authorized = False
        try:
            event, user = _load_token(token, "book")
        except Exception:
            logger.exception(f"Error loading token {token} during book")
            messages.error(
                self.request, "Une erreur est survenue lors de votre requête"
            )
            return reverse("event:list")

        try:
            id_current_user = self.request.user.id
            current_user = CustomUser.objects.get(id=id_current_user)
            if current_user in (
                event.organization.actives.all().union(
                    event.organization.volunteers.all(), event.organization.admins.all()
                )
            ):
                is_authorized = True
        except Exception:
            pass
        next_url = self.request.GET.get("redirect")
        if not utils.is_valid_path(next_url):
            if user:
                user_pk = user.pk
            else:
                user_pk = id_current_user
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

        conditions = event.conditions.all()
        unbook_token = tokenize(user, event, "cancel")
        cancel_url = reverse("event:cancel_reservation", args=[unbook_token])
        cancel_url = self.request.build_absolute_uri(cancel_url)
        register_url = reverse("password_reset")
        register_url = self.request.build_absolute_uri(register_url)

        event_url = reverse("event:detail", args=[event.id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        msg_plain = render_to_string("event/mail/book.txt", context=locals())
        msg_html = render_to_string("event/mail/book.html", context=locals())

        date = event.date.strftime("%d %B")
        subject = (
            f"Votre réservation du {date} pour {event.activity.name}"
            f" à {event.location.name}"
        )

        send_mail(
            subject,
            msg_plain,
            f"{event.organization}" "<no-reply@atelier-soude.fr>",
            [user.email],
            html_message=msg_html,
        )

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
        event_url = reverse("event:detail", args=[event.id, event.slug])
        event_url = self.request.build_absolute_uri(event_url)

        if user.first_name == "":
            # This is a temporary user created only for this event, we can
            # delete it
            user.delete()
        else:
            book_token = tokenize(user, event, "book")
            book_url = reverse("event:book", args=[book_token])
            book_url = self.request.build_absolute_uri(book_url)

        msg_plain = render_to_string("event/mail/unbook.txt", context=locals())
        msg_html = render_to_string("event/mail/unbook.html", context=locals())

        date = event.date.strftime("%d %B")
        subject = (
            f"Confirmation d'annulation pour le " f"{date} à {event.location.name}"
        )

        send_mail(
            subject,
            msg_plain,
            f"{event.organization}" "<no-reply@atelier-soude.fr>",
            [user.email],
            html_message=msg_html,
        )

        messages.success(self.request, "Vous n'êtes plus inscrit à cet évènement")

        next_url = self.request.GET.get("redirect")
        if utils.is_valid_path(next_url):
            return next_url
        return reverse("event:detail", args=[event.id, event.slug])


class PresentView(RedirectView):
    def get(self, request, *args, **kwargs):
        self.event, self.user = _load_token(kwargs["token"], "present")
        res = super().get(request, *args, **kwargs)
        self.event.presents.add(self.user)
        return res

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "event:detail", kwargs={"pk": self.event.pk, "slug": self.event.slug}
        )


class AbsentView(RedirectView):
    def get(self, request, *args, **kwargs):
        self.event, self.user = _load_token(kwargs["token"], "present")
        res = super().get(request, *args, **kwargs)
        self.event.presents.remove(self.user)
        return res

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "event:detail", kwargs={"pk": self.event.pk, "slug": self.event.slug}
        )
