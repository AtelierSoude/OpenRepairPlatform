from django.shortcuts import render, get_list_or_404
from .forms import CustomUserChangeForm, CustomUserCreationForm, UserForm
from .models import CustomUser
from plateformeweb.models import Event
from django.views.generic import ListView, FormView, CreateView, DetailView
from django.contrib.auth.models import PermissionsMixin
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property

# Create your views here.

from django.db.models.signals import post_save
from actstream import action

from django.core.mail import send_mail



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
            action.send(request.user, verb="a modifié ses informations")        
        return render(request,
                      'users/user_profile.html',
                      {'user_form': user_form})

def list_users(request):
    if request.method == 'GET':
        return render(request,
                      'users/user_profile.html', {
                          'user_form': UserForm(instance=request.user,
                                                label_suffix="",
                                                auto_id="field_id_%")})
    else:
        return


## doc : https://stackoverflow.com/questions/26347725/django-custom-user-creation-form

def register(request):

    form = CustomUserCreationForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():

            new_user = form.save()
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1'],
                                    )
            action.send(new_user, verb="a créé un compte")        
            login(request, new_user)
            return HttpResponseRedirect(reverse("user_profile"))


    return render(request, 'users/user_create.html', {'form': form})


class UserDetailView(DetailView):
    model = CustomUser
    context_object_name = 'target_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['attending_events'] = Event.objects.all()
        user = context['target_user']
        attendees = Event.objects.filter(attendees=user)
        context['attending_events'] = attendees
        return context


class UserListView(ListView):
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "user"
        return context
