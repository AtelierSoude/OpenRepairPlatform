from django.shortcuts import render
from django.views.generic import DetailView, ListView, FormView, CreateView, \
    UpdateView
from .models import Organization
from django.urls import reverse


def homepage(request):
    return render(request, 'plateformeweb/home.html')


class OrganizationView(DetailView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrganizationListView(ListView):
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# --- edit ---

class OrganizationFormView():
    model = Organization
    fields = ["name", "active"]

    def get_success_url(self):
        return reverse('organization_detail', args=(self.object.pk,))


class OrganizationCreateView(OrganizationFormView, CreateView):
    pass


class OrganizationEditView(OrganizationFormView, UpdateView):
    pass

# ------


