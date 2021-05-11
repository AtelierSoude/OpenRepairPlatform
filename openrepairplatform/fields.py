import bleach
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField


class CleanHTMLField(HTMLField):
    def clean(self, value, model_instance):
        value = super().clean(value, model_instance).replace("\r", "")
        value = value.replace("<br />", "<br>")
        ALLOWED_TAGS = [
            "a",
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
            "span",
        ]
        ALLOWED_ATTRS = [
            "style",
            "href",
        ]
        ALLOWED_STYLES = [
            "text-decoration",
            "text-decoration-line",
        ]
        cleaned_value = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
            styles=ALLOWED_STYLES,
            strip=True,
        )
        if cleaned_value != value:
            raise ValidationError("Le format n'est pas autorisé.")
        return value
