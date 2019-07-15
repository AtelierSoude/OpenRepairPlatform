import datetime
import pytest
from django.contrib.auth import get_user
from django.core import signing
from django.urls import reverse
from django.utils import timezone

from ateliersoude.event.models import Event
from ateliersoude.user.factories import USER_PASSWORD
from ateliersoude.user.models import CustomUser, Membership, Fee

pytestmark = pytest.mark.django_db


def _django_date(datetime):
    return str(datetime).split(".")[0]


@pytest.fixture
def event_data(
    condition_factory, activity, custom_user_factory, place, organization
):
    cond1 = condition_factory(organization=organization)
    cond2 = condition_factory(organization=organization)
    user1 = custom_user_factory()
    user2 = custom_user_factory()
    user3 = custom_user_factory()
    user4 = custom_user_factory()
    organization.actives.add(user1, user2, user3, user4)
    return {
        "organization": organization,
        "conditions": [cond1.pk, cond2.pk],
        "published": False,
        "publish_at": _django_date(timezone.now()),
        "activity": activity.pk,
        "starts_at": timezone.now().time().strftime("%H:%M"),
        "ends_at": (
            (timezone.now() + datetime.timedelta(hours=4))
            .time()
            .strftime("%H:%M")
        ),
        "date": timezone.now().date().strftime("%Y-%m-%d"),
        "available_seats": 12,
        "registered": [user1.pk, user2.pk, user3.pk],
        "presents": [user1.pk, user2.pk],
        "organizers": [user4.pk],
        "location": place.pk,
    }


def test_event_list(client, event_factory, published_event_factory):
    response = client.get(reverse("event:list"))
    assert response.status_code == 200
    assert get_user(client).is_anonymous
    assert "Aucun évènement trouvé" in response.content.decode()
    unpublished_event = event_factory()
    event1 = published_event_factory()
    event2 = published_event_factory()
    response = client.get(reverse("event:list"))
    html = response.content.decode()
    assert unpublished_event.activity.name not in html
    assert unpublished_event.activity.description not in html
    assert event1 in response.context_data["object_list"]
    assert event2 in response.context_data["object_list"]


def test_event_list_invalid(client, published_event_factory):
    event1 = published_event_factory()
    event2 = published_event_factory()
    response = client.get(reverse("event:list") + "?activity=99")
    assert event1 in response.context_data["object_list"]
    assert event2 in response.context_data["object_list"]


def test_event_list_filter_place(
    client, place_factory, published_event_factory
):
    place1 = place_factory()
    place2 = place_factory()
    event1 = published_event_factory(location=place1)
    event2 = published_event_factory(location=place2)
    response = client.get(reverse("event:list") + f"?place={place1.pk}")
    assert event1 in response.context_data["object_list"]
    assert event2 not in response.context_data["object_list"]


def test_event_list_filter_orga(
    client, organization_factory, published_event_factory
):
    orga1 = organization_factory()
    orga2 = organization_factory()
    event1 = published_event_factory(organization=orga1)
    event2 = published_event_factory(organization=orga2)
    response = client.get(reverse("event:list") + f"?organization={orga1.pk}")
    assert event1 in response.context_data["object_list"]
    assert event2 not in response.context_data["object_list"]


def test_event_list_filter_activity(
    client, activity_factory, published_event_factory
):
    activity1 = activity_factory(name="hello")
    activity2 = activity_factory(name="world")
    event1 = published_event_factory(activity=activity1)
    event2 = published_event_factory(activity=activity2)
    response = client.get(reverse("event:list") + f"?activity={activity1.pk}")
    assert event1 in response.context_data["object_list"]
    assert event2 not in response.context_data["object_list"]


def test_event_list_filter_start_time(client, published_event_factory):
    now = timezone.now()
    old = now - datetime.timedelta(days=3)
    future = now + datetime.timedelta(days=3)
    starts_before = (
        (now + datetime.timedelta(days=1)).date().strftime("%Y-%m-%d")
    )
    starts_after = (
        (now - datetime.timedelta(days=1)).date().strftime("%Y-%m-%d")
    )
    event1 = published_event_factory(date=now.date())
    event2 = published_event_factory(date=old.date())
    event3 = published_event_factory(date=future.date())
    response = client.get(
        reverse("event:list") + f"?starts_before={starts_before}"
        f"&starts_after={starts_after}"
    )
    html = response.content.decode()
    assert event1 in response.context_data["object_list"]
    assert event2.activity.description not in html
    assert event3.activity.description not in html


def test_event_detail_context(client, event, custom_user_factory, user_log):
    anonymous_user = custom_user_factory(first_name="")
    event.registered.add(anonymous_user)
    response = client.get(reverse("event:detail", args=[event.pk, event.slug]))
    assert response.status_code == 200
    assert user_log.email in {
        user[1] for user in response.context_data["users"]
    }
    assert isinstance(response.context_data["event"], Event)
    assert event.pk == response.context_data["event"].pk
    assert event.activity.name in str(response.context_data["event"])


def test_get_event_delete(client, user_log, event):
    response = client.get(reverse("event:delete", args=[event.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:delete", args=[event.pk]))
    assert response.status_code == 403
    current_user = get_user(client)
    event.organization.admins.add(current_user)
    assert current_user in event.organization.admins.all()
    response = client.get(reverse("event:delete", args=[event.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert event.activity.name in html
    assert event.organization.name in html


def test_event_delete(client, user_log, event):
    assert Event.objects.count() == 1
    response = client.post(reverse("event:delete", args=[event.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.post(reverse("event:delete", args=[event.pk]))
    assert response.status_code == 403
    current_user = get_user(client)
    event.organization.admins.add(current_user)
    assert current_user in event.organization.admins.all()
    response = client.post(reverse("event:delete", args=[event.pk]))
    assert Event.objects.count() == 0
    assert response.status_code == 302
    assert response["Location"] == reverse("event:list")


def test_get_event_create(client, user_log, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.get(reverse("event:create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Création d'un nouvel évènement" in html


def test_get_event_create_403(client, user_log, organization):
    response = client.get(reverse("event:create", args=[organization.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas actif" in html


def test_get_event_create_403_not_in_orga(client_log, organization):
    response = client_log.get(reverse("event:create", args=[organization.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas actif" in html


def test_event_create(client, user_log, event_data):
    organization = event_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Event.objects.count() == 0
    response = client.post(
        reverse("event:create", args=[organization.pk]), event_data
    )
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 1
    assert response["Location"] == reverse(
        "event:detail", args=[events[0].pk, events[0].slug]
    )


def test_event_create_invalid(client, user_log, event_data):
    organization = event_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    assert Event.objects.count() == 0
    data = event_data
    del data["starts_at"]
    response = client.post(
        reverse("event:create", args=[organization.pk]), data
    )
    html = response.content.decode()
    assert response.status_code == 200
    assert Event.objects.count() == 0
    assert "Ce champ est obligatoire." in html


def test_get_event_update(client, user_log, event, organization):
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    response = client.get(reverse("event:edit", args=[event.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert f"Mise à jour de '" in html
    assert event.activity.name in html


def test_event_update(client, user_log, event, event_data):
    organization = event_data.pop("organization")
    client.login(email=user_log.email, password=USER_PASSWORD)
    organization.admins.add(user_log)
    event_data["available_seats"] = 10
    response = client.post(reverse("event:edit", args=[event.pk]), event_data)
    events = Event.objects.all()
    assert response.status_code == 302
    assert len(events) == 1
    assert events[0].available_seats == 10
    assert response["Location"] == reverse(
        "event:detail", args=[events[0].pk, events[0].slug]
    )


def test_get_event_update_403(client, user_log, organization, event):
    response = client.get(reverse("event:edit", args=[event.pk]))
    assert response.status_code == 302
    client.login(email=user_log.email, password=USER_PASSWORD)
    response = client.get(reverse("event:edit", args=[event.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas actif" in html


def test_get_event_update_403_not_in_orga(client_log, organization, event):
    response = client_log.get(reverse("event:edit", args=[event.pk]))
    html = response.content.decode()
    assert response.status_code == 403
    assert "pas actif" in html


def test_cancel_reservation_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:cancel_reservation", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_cancel_reservation(client, event, custom_user):
    event.registered.add(custom_user)
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 1
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="cancel"
    )
    resp = client.get(reverse("event:cancel_reservation", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 0


def test_cancel_reservation_temp_user(client, event, custom_user):
    custom_user.first_name = ""
    custom_user.save()
    event.registered.add(custom_user)
    assert Event.objects.first().registered.count() == 1
    assert CustomUser.objects.count() == 1
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="cancel"
    )
    resp = client.get(reverse("event:cancel_reservation", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    assert Event.objects.first().registered.count() == 0
    assert CustomUser.objects.count() == 0


def test_cancel_reservation_redirect(client, event, custom_user):
    event.registered.add(custom_user)
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="cancel"
    )
    query_params = "?redirect=/location/"
    resp = client.get(
        reverse("event:cancel_reservation", args=[token]) + query_params
    )
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")


def test_book_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:book", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_book_no_more_room_by_anonymous(client, event, custom_user):
    event.available_seats = 0
    event.save()
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 0
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="book"
    )
    resp = client.get(reverse("event:book", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 0


def test_book_no_more_room_by_active_volunteer_or_admin(
        client, user_log_staff, event, custom_user):
    client.login(email=user_log_staff.email, password=USER_PASSWORD)
    o = event.organization
    container = [o.actives, o.volunteers, o.admins]
    for status in container:
        event.available_seats = 0
        event.registered.set([])
        event.save()
        [status.set([]) for status in container]
        status.add(user_log_staff)
        o.save()
        nb_registered = Event.objects.first().registered.count()
        assert nb_registered == 0
        token = signing.dumps(
            {"user_id": custom_user.id, "event_id": event.id}, salt="book"
        )
        resp = client.get(reverse("event:book", args=[token]))
        assert resp.status_code == 302
        assert resp["Location"] == reverse(
            "event:detail", args=[event.id, event.slug]
        )
        nb_registered = Event.objects.first().registered.count()
        assert nb_registered == 1


def test_book(client, event, custom_user):
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 0
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="book"
    )
    resp = client.get(reverse("event:book", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    nb_registered = Event.objects.first().registered.count()
    assert nb_registered == 1
    resp = client.get(reverse("event:book", args=[token]))


def test_book_redirect(client, event, custom_user):
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="book"
    )
    query_params = "?redirect=/location/"
    resp = client.get(reverse("event:book", args=[token]) + query_params)
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")


def test_user_absent_wrong_token(client):
    token = signing.dumps({"user_id": 1, "event_id": 2}, salt="unknown")
    resp = client.get(reverse("event:user_absent", args=[token]))
    assert resp.status_code == 302
    assert resp["Location"] == reverse("event:list")


def test_user_absent(client, event, custom_user):
    event.presents.add(custom_user)
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 1
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="absent"
    )
    resp = client.get(reverse("event:user_absent", args=[token]))
    assert resp.status_code == 302
    assert (
        resp["Location"]
        == reverse("event:detail", args=[event.id, event.slug]) + "#manage"
    )
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 0


def test_user_absent_remove_contribution(
    client, event, custom_user, participation_factory, membership_factory
):
    participation_factory(event=event, user=custom_user, amount=10, saved=True)
    membership = membership_factory(
        organization=event.organization, user=custom_user, amount=10
    )
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 1
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="absent"
    )
    _ = client.get(reverse("event:user_absent", args=[token]))
    nb_presents = Event.objects.first().presents.count()
    assert nb_presents == 0
    membership.refresh_from_db()
    assert membership.amount == 0


def test_user_absent_redirect(client, event, custom_user):
    token = signing.dumps(
        {"user_id": custom_user.id, "event_id": event.id}, salt="absent"
    )
    query_params = "?redirect=/location/"
    resp = client.get(
        reverse("event:user_absent", args=[token]) + query_params
    )
    assert resp.status_code == 302
    assert resp["Location"] == reverse("location:list")


def test_close_event(
    client,
    organization,
    event_factory,
    custom_user_factory,
    participation_factory,
    membership_factory,
):
    active = custom_user_factory()
    organization.actives.add(active)
    event = event_factory(organization=organization)
    member = custom_user_factory()
    member2 = custom_user_factory()
    visitor_present = custom_user_factory()
    visitor_absent = custom_user_factory()
    visitor_present.first_name = ""
    visitor_absent.first_name = ""
    visitor_present.save()
    visitor_absent.save()
    event.registered.add(visitor_absent)
    first_participation = participation_factory(
        event=event, user=visitor_present, amount=20
    )
    participation_factory(event=event, user=member, amount=10, saved=True)
    participation_factory(event=event, user=member2, amount=10)
    membership_member = membership_factory(
        user=member, organization=event.organization, amount=15
    )
    membership_member2 = membership_factory(
        user=member2,
        organization=event.organization,
        amount=50,
        first_payment=timezone.now() - datetime.timedelta(days=400),
    )
    assert organization.members.count() == 2
    assert CustomUser.objects.count() == 5
    assert Fee.objects.count() == 0

    resp = client.post(reverse("event:close", args=[event.pk]))
    assert resp.status_code == 302
    client.login(email=member.email, password=USER_PASSWORD)
    resp = client.post(reverse("event:close", args=[event.pk]))
    assert resp.status_code == 403
    client.login(email=active.email, password=USER_PASSWORD)
    resp = client.post(reverse("event:close", args=[event.pk]))
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    organization.refresh_from_db()
    first_participation.refresh_from_db()
    membership_member.refresh_from_db()
    membership_member2.refresh_from_db()
    visitor_membership = Membership.objects.filter(
        user=visitor_present
    ).first()
    assert first_participation.saved
    assert visitor_membership.amount == 20
    assert membership_member.amount == 15
    assert membership_member2.amount == 10
    assert organization.members.count() == 3
    assert Fee.objects.count() == 3
    assert CustomUser.objects.count() == 4


def test_add_active_event(
    client, organization, event_factory, custom_user_factory
):
    user = custom_user_factory()
    active = custom_user_factory()
    organization.actives.add(active)
    event = event_factory(organization=organization)
    assert event.organizers.count() == 0
    resp = client.post(reverse("event:add_active", args=[event.pk]))
    assert resp.status_code == 302
    client.login(email=user.email, password=USER_PASSWORD)
    resp = client.post(reverse("event:add_active", args=[event.pk]))
    assert resp.status_code == 403
    client.login(email=active.email, password=USER_PASSWORD)
    resp = client.post(reverse("event:add_active", args=[event.pk]))
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    event.refresh_from_db()
    assert event.organizers.count() == 1


def test_remove_active_event(
    client, organization, event_factory, custom_user_factory
):
    user = custom_user_factory()
    active = custom_user_factory()
    organization.actives.add(active)
    event = event_factory(organization=organization)
    event.organizers.add(active)
    assert event.organizers.count() == 1
    resp = client.post(reverse("event:remove_active", args=[event.pk]))
    assert resp.status_code == 302
    client.login(email=user.email, password=USER_PASSWORD)
    resp = client.post(reverse("event:remove_active", args=[event.pk]))
    assert resp.status_code == 403
    client.login(email=active.email, password=USER_PASSWORD)
    resp = client.post(reverse("event:remove_active", args=[event.pk]))
    assert resp["Location"] == reverse(
        "event:detail", args=[event.id, event.slug]
    )
    event.refresh_from_db()
    assert event.organizers.count() == 0
