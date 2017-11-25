from django.shortcuts import render
from .forms import CustomUserChangeForm, CustomUserCreationForm, UserForm
from .models import CustomUser


# Create your views here.


def user_profile(request):
    if request.method == 'GET':
        return render(request,
                      'users/user_profile.html', {
                          'user_form': UserForm(instance=request.user,
                                                label_suffix="",
                                                auto_id="field_id_%")})
    else:
        user_form = UserForm(request.POST,
                             instance=CustomUser.objects.get(id=request.user.id))
        if user_form.is_valid():
            user_form.save()
        return render(request,
                      'users/user_profile.html',
                      {'user_form': user_form})
