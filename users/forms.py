from address.forms import AddressField
from datetime import date
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import django.forms.widgets as widgets


from .models import CustomUser

# TODO: issue with 2 following forms, only the 3rd one works
class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserCreationForm, self).__init__(*args, **kargs)
        #del self.fields['username']

    class Meta:
        model = CustomUser
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        #del self.fields['username']

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number',
                          'street_address', 'birth_date', 'avatar_img', 'bio']

# works OK
class UserForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number',
                  'street_address', 'birth_date', 'avatar_img', 'bio']
        widgets = {
            'birth_date': widgets.SelectDateWidget(years=range(1900, date.today().year + 1)),

            # TODO: possible to switch to a jquery datepicker once the localization
            # issue is fixed (see the user profile form, and base.html
            #
            # 'birth_date': forms.DateInput(attrs={'class':'datepicker'}),

            'email': widgets.EmailInput(attrs={'type':'email'}),
            'phone_number': widgets.TextInput(attrs={'type':'tel', 'placeholder': '+336012345678'}),
        }
        localized_fields = ['birth_date']
