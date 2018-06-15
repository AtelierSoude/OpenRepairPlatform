from django.test import TestCase
from plateformeweb.models import PlaceType

class TestPlaceTypeModel(TestCase):
    "place type tests"

    def setUp(self):
        PlaceType.objects.create(name="Atelier Soudé", slug="ateliersoude")

    def test_place_type(self):
        slug = "ateliersoude"
        latelier = PlaceType.objects.get(slug=slug)
        self.assertEqual(latelier.slug, slug)
        self.assert(latelier.name)
