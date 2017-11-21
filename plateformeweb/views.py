from django.shortcuts import render
from .forms import UserForm
from .models import User

def homepage(request):
    return render(request, 'plateformeweb/home.html')

def user_profile(request):
    if request.method == 'GET':
        return render(request, 'plateformeweb/user_profile.html', {
            'user_form': UserForm(instance=request.user, label_suffix="", )})
    else:
        user_form = UserForm(request.POST, instance=User.objects.get(id=request.user.id))
        if user_form.is_valid():
            user_form.save()
        return render(request, 'plateformeweb/user_profile.html',
                          {'user_form': user_form})
