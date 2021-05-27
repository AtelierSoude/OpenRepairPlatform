from datetime import date, datetime
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import DetailView

from html2text import html2text
from ics import Calendar as ICSCalendar
from ics import Event as ICSEvent
from ics import Organizer

from openrepairplatform.user.models import Organization


class EventByOrganizationICSView(DetailView):
    model = Organization

    def get(self, request, *args, **kwargs):
        organization = self.get_object()
        events = []

        for event in organization.events.filter(date__gte=date.today()):
            organizer = Organizer(
                common_name=organization.name,
                email=organization.email,
            )
            event_url = request.build_absolute_uri(
                reverse("event:detail", kwargs={"pk": event.pk, "slug": event.slug})
            )
            events.append(
                ICSEvent(
                    name=str(event),
                    begin=datetime.combine(event.date, event.starts_at),
                    end=datetime.combine(event.date, event.ends_at),
                    organizer=organizer,
                    url=event_url,
                    location=event.location.name,
                    description=html2text(event.description),
                )
            )

        ics_calendar = ICSCalendar(events=events)

        response = HttpResponse(
            str(ics_calendar), content_type="application/force-download"
        )
        response[
            "Content-Disposition"
        ] = f"attachment; filename={organization.slug}.ics"
        return response
