from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django import urls
from django.shortcuts import render, reverse


@login_required
def home(request):
    return HttpResponseRedirect(reverse('homepage'))
