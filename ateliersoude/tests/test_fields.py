import pytest
from django.core.exceptions import ValidationError

from ateliersoude.fields import CleanHTMLField
from ateliersoude.location.models import Place

pytestmark = pytest.mark.django_db


def test_html_field():
    field = CleanHTMLField()
    with pytest.raises(ValidationError):
        field.clean("<script>alert(0)</script>", Place)
