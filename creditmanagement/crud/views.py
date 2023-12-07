from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Subject
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .forms import SignUpForm
from django.db.models import Sum

class TopView(TemplateView):
  template_name= "top.html"

class SubjectListView(LoginRequiredMixin, ListView):
  model = Subject
  paginate_by = 8

class SubjectCreateView(LoginRequiredMixin, CreateView):
  model = Subject
  fields = '__all__'

class SubjectUpdateView(LoginRequiredMixin, UpdateView):
  model = Subject
  fields = '__all__'
  template_name_suffix = '_update_form'

class SubjectDeleteView(LoginRequiredMixin, DeleteView):
  model = Subject
  success_url = reverse_lazy('list')

class LoginView(LoginView):
  form_class = AuthenticationForm
  template_name ='login.html'
  success_url = reverse_lazy('list')

class LogoutView(LoginRequiredMixin, LogoutView):
  template_name = 'top.html'

class SignUpView(CreateView):
  form_class = SignUpForm
  template_name = "crud/signup.html"
  success_url = reverse_lazy('list')

  def form_valid(self, form):
    user = form.save()
    login(self.request, user)
    self.object = user 
    return HttpResponseRedirect(self.get_success_url())
  
def calculate_total(request):
    total_credit = Subject.objects.aggregate(Sum('credit'))['credit__sum']
    return render(request, 'total.html', {'total_credit': total_credit})
