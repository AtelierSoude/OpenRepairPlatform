from django.shortcuts import render, get_list_or_404
from .forms import CustomUserChangeForm, CustomUserCreationForm, UserForm
from .models import CustomUser
from django.views.generic.list import ListView


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

        events = PublishedEvent.objects.filter(
        starts_at__gte=timezone.now()).order_by('starts_at')[:10]
    context = {"events": events}
    

def list_users(request):
    if request.method == 'GET':
        return render(request,
                      'users/user_profile.html', {
                          'user_form': UserForm(instance=request.user,
                                                label_suffix="",
                                                auto_id="field_id_%")})
    else:
        return


class UserListView(ListView):

    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "user"
        return context

