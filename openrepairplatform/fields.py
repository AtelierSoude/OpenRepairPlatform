import bleach
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField


class CleanHTMLField(HTMLField):
    def clean(self, value, model_instance):
        value = super().clean(value, model_instance).replace("\r", "")
        value = value.replace("<br />", "<br>")
        ALLOWED_TAGS = [
            'a', 'abbr', 'acronym', 'address', 'area', 'aria-label', 'b', 'big',
            'blockquote', 'br', 'caption', 'center', 'cite', 'code', 'col',
            'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em',
            'font', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
            'ins', 'kbd', 'label', 'legend', 'li', 'map', 'menu', 'ol',
            'p', 'pre', 'q', 's', 'samp', 'small', 'span', 'strike',
            'strong', 'sub', 'sup', 'u', 'ul', 'var', 'section', 'article', 'div'
        ]
        ALLOWED_ATTRS = [
            "style",
            "href",
            "class",
        ]
        ALLOWED_STYLES = [
            "text-decoration",
            "text-decoration-line",
            "color",
        ]
        cleaned_value = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
            styles=ALLOWED_STYLES,
            strip=True
        )
        if cleaned_value != value:
            raise ValidationError("Le format n'est pas autorisé.")
        return value
