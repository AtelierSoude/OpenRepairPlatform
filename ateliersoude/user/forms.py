from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

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
            "birth_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            )
        }


class CustomUserEmailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class MoreInfoCustomUserForm(forms.ModelForm):
    amount_paid = forms.IntegerField(min_value=0, initial=0)

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
