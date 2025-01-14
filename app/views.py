from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin  # Ensures only logged-in users can access views
from django.urls import reverse_lazy
from .models import Commission
from .forms import CommissionForm



class HomeView(TemplateView):
    template_name = 'app/home.html'


class AboutPageView(TemplateView):
    template_name = 'app/about.html'


class CommissionListView(ListView):
    model = Commission
    template_name = 'app/commission_list.html'
    context_object_name = 'commissions'


class CommissionCreateView(LoginRequiredMixin, CreateView):
    model = Commission
    form_class = CommissionForm  # Use the custom form here
    template_name = 'app/commission_form.html'
    success_url = reverse_lazy('commission_list')  # Update with your URL name if different

    def form_valid(self, form):
        # Automatically set 'commissioner' to the logged-in user
        form.instance.commissioner = self.request.user
        return super().form_valid(form)


class CommissionDetailView(DetailView):
    model = Commission
    template_name = 'app/commission_detail.html'


class CommissionUpdateView(UpdateView):
    model = Commission
    fields = ['title', 'description', 'price', 'available']  # Add fields to allow for updates
    template_name = 'app/commission_form.html'
    success_url = reverse_lazy('commission_list')


class CommissionDeleteView(DeleteView):
    model = Commission
    template_name = 'app/commission_confirm_delete.html'
    success_url = reverse_lazy('commission_list')
