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
    kyoutu = Category.objects.filter(name = "共通教養科目")
    rest_credit = 128 - total_credit 
    return render(request, 'total.html', {'total_credit': total_credit, 'rest_credit': rest_credit, 'kyoutu': kyoutu})

def graduation_requirements(request):
    #student = Student.objects.get()
    
    # カテゴリーごとの単位を数える
    category_credits = {}
    for category in Category.objects.all():
        category_credits[category.name] = category.subject_set.aggregate(total_credits=Sum('credit'))['total_credits'] or 0
    
    # カテゴリーごとの必要な単位数
    required_credits = {
        '学科共通科目': 10,
        '専門科目': 128,
        # 他のカテゴリーも追加
    }
    
    # 卒業までの残りの単位数
    remaining_credits = {}
    for category, required_credit in required_credits.items():
        remaining_credit = required_credit - category_credits.get(category, 0)
        if remaining_credit > 0:
            remaining_credits[category] = remaining_credit
    
    return render(request, 'total.html', {'remaining_credits': remaining_credits})
