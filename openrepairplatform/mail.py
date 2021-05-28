from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from openrepairplatform.event.templatetags.app_filters import tokenize


def event_send_mail(
    event,
    user,
    subject,
    text_template,
    html_template,
    from_email: str,
    to_email: list,
    request=False,
    base_url=False,
    role=False,
):

    """ Generic method to send mail """

    if not request and not base_url:
        raise ReferenceError(
            "Vous devez renseigner une url ou passer la requête à cette méthode."
        )
    elif request and base_url:
        raise ReferenceError(
            "Vous ne pouvez pas passer une url et la requête en même temps,"
            " c'est l'un ou l'autre."
        )

    unbook_token = tokenize(user, event, "cancel")
    book_token = tokenize(user, event, "book")
    cancel_url = reverse("event:cancel_reservation", args=[unbook_token])
    register_url = reverse("password_reset")
    event_url = reverse("event:detail", args=[event.id, event.slug])
    book_url = reverse("event:book", args=[book_token])

    if base_url:
        cancel_url = base_url + cancel_url
        register_url = base_url + register_url
        event_url = base_url + event_url
        book_url = base_url + book_url
    else:
        register_url = request.build_absolute_uri(register_url)
        event_url = request.build_absolute_uri(event_url)
        cancel_url = request.build_absolute_uri(cancel_url)
        book_url = request.build_absolute_uri(book_url)

    conditions = event.conditions.all()

    text_content = render_to_string(text_template, context=locals())
    html_content = render_to_string(html_template, context=locals())

    mail = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    mail.attach_alternative(html_content, "text/html")
    mail.send()
