from datetime import date
from typing import Optional
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import resolve, Resolver404, ResolverMatch
from django.utils import timezone

MAX_SIZE_MB = 2


def validate_image(image):
    file_size = image.file.size
    if file_size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"La taille maximale d'une image est de " f"{MAX_SIZE_MB}MB"
        )


def get_future_published_events(events_objects, organization=None):
    """Filters the events to fetch only the future published events"""
    return (
        events_objects.filter(published=True)
        .filter(publish_at__lte=timezone.now())
        .exclude(date__lt=date.today())
        .exclude(date=date.today(), ends_at__lte=timezone.now().time())
        .order_by("date")
    )


def is_valid_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    try:
        # this call throws if the redirect is not registered in urls.py
        resolve(path)
        return True
    except Resolver404:
        return False


def get_referer_resolver(request: HttpRequest) -> Optional[ResolverMatch]:
    """
    Return the referer's ResolverMatch
    """
    referer = request.META.get("HTTP_REFERER")
    if not referer:
        return None

    url = urlparse(referer)
    if url.netloc != request.get_host():
        return None

    if is_valid_path(url.path):
        return resolve(url.path)
    else:
        return None
