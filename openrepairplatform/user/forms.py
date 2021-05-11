from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from datetime import date as dt
from dal import autocomplete

from .models import CustomUser, Organization


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class UserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "street_address"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "avatar_img",
            "phone_number",
            "street_address",
            "birth_date",
            "gender",
            "bio",
            "is_visible",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")
        }


class CustomUserEmailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class CustomUserSearchForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label="Veuillez rechercher si l'utilisateur existe avant de le créer",
        widget=autocomplete.ModelSelect2(
            url="user_autocomplete",
            attrs={"data-html": True, "data-allow-clear": "true"},
        ),
    )


class MoreInfoCustomUserForm(forms.ModelForm):
    amount_paid = forms.IntegerField(min_value=0, initial=0)
    payment = forms.ChoiceField(
        choices=[
            (1, "Espèces"),
            (2, "Online"),
            (3, "Chèque"),
            (4, "CB"),
            (5, "Gonettes"),
        ],
        label="Type de paiement",
    )
    date = forms.DateField(
        initial=dt.today(),
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    first_fee = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "street_address"]


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].widget.attrs.update({"class": "form-control"})
        self.fields["fee_description"].widget = forms.TextInput()

    class Meta:
        model = Organization
        exclude = [
            "visitors",
            "members",
            "actives",
            "volunteers",
            "admins",
            "slug",
        ]
