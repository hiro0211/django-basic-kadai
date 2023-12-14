from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView,DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Subject, Category
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

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args, **kwargs)

    context["categories"] = Category.objects.all()
    return context

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

class SubjectDetailView(LoginRequiredMixin, DetailView):
  model = Subject
  context_object_name = 'subject'
  template_name = "crud/subject_detail.html"

class CategorySubjectListView(ListView):
  model = Subject
  template_name = "crud/category_subject.html"
  context_object_name = "subjects"

  def get_queryset(self, **kwargs):
    category_name = self.kwargs["category"]
    category = get_object_or_404(Category, name=category_name)
    return super().get_queryset().filter(category=category)

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
    rest_credit = 128 - total_credit 
    return render(request, 'total.html', {'total_credit': total_credit, 'rest_credit': rest_credit})
"""
def graduation_requirements(request):
    #student = Student.objects.get()
    
    # カテゴリーごとの単位を数える
    category_credits = {}
    for subject in Subject.objects.all():
        if subject.category in category_credits:
            category_credits[subject.category] += subject.credits
        else:
            category_credits[subject.category] = subject.credits
    
    # カテゴリーごとの必要な単位数
    required_credits = {
        'Elective': 10,
        'Core': 20,
        # 他のカテゴリーも追加
    }
    
    # 卒業要件を満たしているかどうかを判定
    requirements_met = all(category_credits.get(category, 0) >= required_credits[category] for category in required_credits)
    
    return render(request, 'graduation_requirements.html', { 'category_credits': category_credits, 'requirements_met': requirements_met})
  """