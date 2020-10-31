import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from openrepairplatform import utils

pytestmark = pytest.mark.django_db


class FileMock:
    def __init__(self, size):
        self.size = size


class ImageMock:
    def __init__(self, size):
        self.file = FileMock(size=size)


def get_image_file(size=100):
    return ImageMock(size)


def test_validate_image():
    img_valid = get_image_file(size=utils.MAX_SIZE_MB * 1024 * 1024)
    utils.validate_image(img_valid)

    img_invalid = get_image_file(size=utils.MAX_SIZE_MB * 1024 * 1024 + 1)
    with pytest.raises(ValidationError):
        utils.validate_image(img_invalid)


def test_get_referer_resolver_noreferer():
    req = HttpRequest()
    req.META = {"HTTP_REFERER": None, "HTTP_HOST": "monhost"}
    assert utils.get_referer_resolver(req) is None


def test_get_referer_resolver_wrong_netloc():
    req = HttpRequest()
    req.META = {"HTTP_REFERER": "http://monhost2/test", "HTTP_HOST": "monhost"}
    settings.ALLOWED_HOSTS.append("monhost")
    assert utils.get_referer_resolver(req) is None


def test_get_referer_resolver_404():
    req = HttpRequest()
    req.META = {
        "HTTP_REFERER": "http://monhost/bla/bla/bla",
        "HTTP_HOST": "monhost",
    }
    settings.ALLOWED_HOSTS.append("monhost")
    assert utils.get_referer_resolver(req) is None


def test_get_referer_resolver():
    req = HttpRequest()
    req.META = {
        "HTTP_REFERER": "http://monhost/event/",
        "HTTP_HOST": "monhost",
    }
    settings.ALLOWED_HOSTS.append("monhost")
    assert utils.get_referer_resolver(req).route == "event/"
