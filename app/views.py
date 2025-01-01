from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Commission

class HomeView(TemplateView):
    template_name = 'app/home.html'

class AboutPageView(TemplateView):
    template_name = 'app/about.html'

class CommissionListView(ListView):
    model = Commission
    template_name = 'app/commission_list.html'
    context_object_name = 'commissions'

class CommissionCreateView(CreateView):
    model = Commission
    fields = ['title', 'description', 'price']  # Add fields that match your model
    template_name = 'app/commission_form.html'
    success_url = reverse_lazy('commission-list')

class CommissionDetailView(DetailView):
    model = Commission
    template_name = 'app/commission_detail.html'

class CommissionUpdateView(UpdateView):
    model = Commission
    fields = ['title', 'description', 'price']  # Add fields that match your model
    template_name = 'app/commission_form.html'
    success_url = reverse_lazy('commission-list')

class CommissionDeleteView(DeleteView):
    model = Commission
    template_name = 'app/commission_confirm_delete.html'
    success_url = reverse_lazy('commission-list')
