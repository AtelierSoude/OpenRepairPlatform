import logging
from datetime import timedelta

from django.utils.timezone import now
from django.contrib.gis.geos import Point
from django.core.management import BaseCommand

from openrepairplatform.event import factories as event_factories
from openrepairplatform.user import factories as user_factories

from openrepairplatform.user.models import CustomUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create mock data"

    def handle(self, **options):
        logger.info("Creating mock data")

        logger.info("Creating users")
        for _ in range(10):
            user_factories.CustomUserFactory()

        logger.info("Giving a name & surname to the superuser")
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        admin_user.first_name = "Admin"
        admin_user.last_name = "User"
        admin_user.save()

        logger.info("Creating 'Organization'")
        test_organization = user_factories.OrganizationFactory(
            name="Test Organization",
            description="Test description",
        )
        test_organization.admins.add(admin_user)

        logger.info("Creating 'Place' hotel de ville in Lyon")
        lyon_hotel_de_ville = event_factories.PlaceFactory(
            organization=test_organization,
            location=Point(4.834419469403489, 45.768028703688145),
            name="Hôtel de Ville, Lyon",
            address="1 Pl. de la Comédie, 69001 Lyon, France",
        )

        logger.info("Creating an 'Event' for right now in Lyon")
        event_factories.EventFactory(
            published=True,
            location=lyon_hotel_de_ville,
            organization=test_organization,
            date=now().date(),
            starts_at=now().time(),
            ends_at=(now() + timedelta(hours=3)).time(),
        )

        logger.info("Creating other 'Events'")
        for _ in range(20):
            event_factories.EventFactory(published=True)
