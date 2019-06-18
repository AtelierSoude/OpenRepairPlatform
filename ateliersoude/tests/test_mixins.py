import pytest
from django.views.generic import DeleteView

from ateliersoude.mixins import RedirectQueryParamView

pytestmark = pytest.mark.django_db
DEFAULT_PATH = "/default/"


class RequestMock:
    def __init__(self, get={}):
        self.GET = get


class ObjModelMock:
    pass


class TestView(RedirectQueryParamView, DeleteView):
    success_url = DEFAULT_PATH
    object = ObjModelMock()


def test_redirect_view():
    redirect_view = TestView()
    redirect_view.request = RequestMock(get={"redirect": "/event/"})
    redirect_path = redirect_view.get_success_url()
    assert redirect_path == "/event/"


def test_redirect_view_no_forward_slash():
    redirect_view = TestView()
    redirect_view.request = RequestMock(get={"redirect": "/event"})
    redirect_path = redirect_view.get_success_url()
    assert redirect_path == DEFAULT_PATH


def test_redirect_view_no_redirect():
    redirect_view = TestView()
    redirect_view.request = RequestMock(get={"something_else": "/event/"})
    redirect_path = redirect_view.get_success_url()
    assert redirect_path == DEFAULT_PATH
