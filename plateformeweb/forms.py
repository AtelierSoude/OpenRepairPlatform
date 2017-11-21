from django.forms import ModelForm
from plateformeweb.models import User


# Create the form class.
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number',
                  'street_address', 'birth_date', 'avatar_img', 'bio']

