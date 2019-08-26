from django.forms import ModelForm
from .models import Stuff


class StuffForm(ModelForm):
    # type = ChoiceField(
    #     choices=(
    #         ("D", "Device"),
    #         ("T", "Tool"),
    #         ("P", "Part"),
    #     )
    # )

    class Meta:
        model = Stuff
        fields = [
            "member_owner",
            "organization_owner",
            "place",
            "state"
        ]
