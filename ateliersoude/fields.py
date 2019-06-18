import bleach
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField


class CleanHTMLField(HTMLField):
    def clean(self, value, model_instance):
        value = super().clean(value, model_instance).replace("\r", "")
        ALLOWED_TAGS = [
            "p",
            "br",
            "b",
            "strong",
            "i",
            "em",
            "u",
            "h1",
            "ul",
            "ol",
            "li",
            "div",
        ]
        cleaned_value = bleach.clean(value, tags=ALLOWED_TAGS, strip=True)
        if cleaned_value != value:
            raise ValidationError("Le format n'est pas autorisé.")
        return value
