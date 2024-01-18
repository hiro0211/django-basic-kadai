from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views import generic
from .models import Subject, Category, Student
from django.urls import reverse_lazy
from django.contrib.auth.views import (LoginView, LogoutView, PasswordContextMixin, PasswordChangeDoneView,
                                      PasswordChangeView, PasswordResetView, PasswordResetDoneView,
                                      PasswordResetConfirmView, PasswordResetCompleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import SignUpForm, SiteAuthDataForm, LoginForm, SignUpForm2
from django.db.models import Sum
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains

class TopView(TemplateView):
  template_name= "top.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["form_name"] = "top"
    return context

class SubjectListView(LoginRequiredMixin, ListView):
  model = Subject
  paginate_by = 24

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args, **kwargs)

    context["categories"] = Category.objects.all()
    return context
  
  def get_queryset(self):
    query = self.request.GET.get('query')

    if query:
      subject_list = Subject.objects.filter(
            name__icontains=query, user=self.request.user)
    else:
      subject_list = Subject.objects.filter(user=self.request.user)
    return subject_list

class SubjectCreateView(LoginRequiredMixin, CreateView):
  model = Subject
  fields = '__all__'

class LoadDataFromSite(generic.FormView):
    template_name= "crud/unipa_register.html"
    form_class = SiteAuthDataForm

    def get(self, request, *args, **kwargs):
        if hasattr(request.user, 'student'):
          #学年を取得する
          user_grade = request.user.student.grade
          user_department = request.user.student.department
          #1年生前期の定積情報を取得
          if user_grade =="1年後期" and user_department == "経済学部":
            
            def form_valid(self, form):
              user_id = form.cleaned_data['user_id']
              password_text = form.cleaned_data['password']
        
              chrome_driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

              chrome_driver.get("https://unipa.itp.kindai.ac.jp/up/faces/login/Com00501A.jsp")
              time.sleep(1)

              mail = chrome_driver.find_element(By.ID, 'form1:htmlUserId') 
              password = chrome_driver.find_element(By.ID, 'form1:htmlPassword')

              mail.clear()
              password.clear()

              mail.send_keys(user_id)
              password.send_keys(password_text)

              button = chrome_driver.find_element(By.ID, 'form1:login')
              button.click()

              #chrome_driver.save_screenshot('screenshot.png')
              target_element = chrome_driver.find_element(By.ID, 'menuc3')
              actions = ActionChains(chrome_driver)
              actions.move_to_element(target_element).perform()

              grade = chrome_driver.find_element(By.ID, 'menuimg3-1')
              time.sleep(2)
              grade.click()

              #1年生前期の成績情報を取得
              fresh_first_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[10]

              Subject.objects.filter(user=self.request.user).delete
              category = '' 
              for tr in fresh_first_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
                try:
                  kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
                  credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
                  score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
                except Exception:
                  pass
                else:
                  if credit:
                    category_ = category
                    if category_ == '外国語科目':
                      if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                        category_ = '第一外国語科目'
                      else:
                        category_ = '第二外国語科目'
                      #print(category, kamoku)
                    category_model , _ = Category.objects.get_or_create(name=category_)
                    Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
                  
                  else:
                    category = kamoku

              return redirect("list")
          
          elif user_grade =="2年前期" and user_department == "経済学部":

    
    def form_valid(self, form):
        user_id = form.cleaned_data['user_id']
        password_text = form.cleaned_data['password']
        # test.pyの内容をこの下に書く
        chrome_driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        #chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")

        # Chromeドライバーを起動
        #chrome_driver = webdriver.Chrome(chrome_options=chrome_options)

        chrome_driver.get("https://unipa.itp.kindai.ac.jp/up/faces/login/Com00501A.jsp")
        time.sleep(1)

        mail = chrome_driver.find_element(By.ID, 'form1:htmlUserId') 
        password = chrome_driver.find_element(By.ID, 'form1:htmlPassword')

        mail.clear()
        password.clear()

        mail.send_keys(user_id)
        password.send_keys(password_text)

        #mail.submit()
        button = chrome_driver.find_element(By.ID, 'form1:login')
        button.click()

        #chrome_driver.save_screenshot('screenshot.png')
        target_element = chrome_driver.find_element(By.ID, 'menuc3')
        actions = ActionChains(chrome_driver)
        actions.move_to_element(target_element).perform()

        grade = chrome_driver.find_element(By.ID, 'menuimg3-1')
        time.sleep(2)
        grade.click()

        #1年生前期の成績情報を取得
        fresh_first_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[10]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in fresh_first_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                #print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku

        #1年生後期の成績情報を取得
        fresh_second_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[12]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in fresh_second_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                #print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku
        #credit_element = chrome_driver.find_element(By.CLASS_NAME, 'tdKyoshokuinNameList')
        #credit = credit_element.text

        # 2年生前期の成績情報を取得
        sopho_first_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[14]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in sopho_first_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                #print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku
        
        #2年生後期の成績情報を取得
        sopho_second_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[16]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in sopho_second_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if 'イングリッシュ' in kamoku or "英語" in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                #print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku
        
        #3年生前期の成績情報を取得
        junior_first_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[18]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in junior_first_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                #print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku
        
        #3年生後期の成績情報を取得
        junior_second_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[20]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in junior_second_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                #print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku
        
        #4年生前期の成績情報を取得
        senior_first_semester = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[22]

        Subject.objects.filter(user=self.request.user).delete
        category = '' 
        for tr in senior_first_semester.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
          try:
            kamoku = tr.find_element(By.CSS_SELECTOR, 'td.kamokuList').text    
            credit = tr.find_element(By.CSS_SELECTOR, 'td.tdTaniList').text
            score = tr.find_element(By.CSS_SELECTOR, 'td.tdSotenList').text
          except Exception:
            pass
          else:
            if credit:
              category_ = category
              if category_ == '外国語科目':
                if '英語' in kamoku or 'イングリッシュ' in kamoku or 'ＴＯＥＩＣ' in kamoku:
                  category_ = '第一外国語科目'
                else:
                  category_ = '第二外国語科目'
                print(category, kamoku)
              category_model , _ = Category.objects.get_or_create(name=category_)
              Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, user=self.request.user)    
            
            else:
              category = kamoku
        

        return redirect("list")
        #chrome_driver.quit()
        #chrome_driver.quit()
    """
    def form_valid(self, form):
      object = form.save(commit=False)
      object.user_name = self.request.user
      object.save()
      return super().form_valid(form)

    def get_success_url(self):
      return resolve_url('list', kwargs={'pk': self.object.id})  
    """
    
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
  form_class = LoginForm
  template_name ='login.html'
  success_url = reverse_lazy('list')

class LogoutView(LoginRequiredMixin, LogoutView):
  template_name = 'top.html'

  def dispatch(self, request, *args, **kwargs):
    logout(request)
    return super().dispatch(request, *args, **kwargs)
  
  def post(self, request, *args, **kwargs):
    return HttpResponseRedirect(reverse_lazy('top'))

class SignUpView(CreateView):
  form_class = SignUpForm
  template_name = "crud/signup.html"
  success_url = reverse_lazy('list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['form2'] = SignUpForm2()
    return context

  def post(self, request, *args, **kwargs):
    self.object = None
    form = self.get_form()
    form2 = SignUpForm2(self.request.POST)
    if form.is_valid() and form2.is_valid():
      return self.form_valid(form, form2)
    else:
      return self.form_invalid(form)
    
  def form_valid(self, form, form2):
    user = form.save()
    login(self.request, user)
    self.object = user
    
    student = form2.save(commit=False)
    student.user = user
    student.save()

    return HttpResponseRedirect(self.get_success_url())

class PasswordChange(LoginRequiredMixin, PasswordChangeView):
  success_url = reverse_lazy('crud:password_change_done')
  template_name = 'crud/password_change.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["form_name"] = "password_change"
    return context

class PasswordReset(PasswordResetView):
  subject_template_name = 'crud/mail_template/reset/subject.txt'
  email_template_name = 'crud/mail_template/reset/message.txt'
  template_name = 'crud/password_reset_form.html'
  success_url = reverse_lazy('crud:password_reset_done')

class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
  template_name = 'crud/password_reset_done.html'

class PasswordResetConfirm(PasswordResetCompleteView):
  success_url = reverse_lazy('crud:password_reset_complete')
  template_name = 'crud/password_reset_confirm.html'

class PasswordResetComplete(PasswordResetCompleteView):
  template_name = 'crud/password_reset_complete.html'

def calculate_total(request):
    filtered_kyoutu = Subject.objects.filter(category_id = 1, user=request.user)
    kyoutu = filtered_kyoutu.aggregate(Sum('credit'))['credit__sum']
    rest_kyoutu = 16 - (kyoutu or 0)

    filtered_first = Subject.objects.filter(category_id = 2, user=request.user)
    first_language = filtered_first.aggregate(Sum('credit'))['credit__sum']
    rest_fisrt = 14 - (first_language or 0)

    filtered_second = Subject.objects.filter(category_id = 3, user=request.user)
    second_language = filtered_second.aggregate(Sum('credit'))['credit__sum']

    filtered_gakubu = Subject.objects.filter(category_id = 4, user=request.user)
    gakubu_subject = filtered_gakubu.aggregate(Sum('credit'))['credit__sum']
    rest_gakubu = 14 - (gakubu_subject or 0)

    filtered_department = Subject.objects.filter(category_id = 5, user=request.user)
    department_subject = filtered_department.aggregate(Sum('credit'))['credit__sum']
    rest_department = 28 - (department_subject or 0)

    filtered_remedical = Subject.objects.filter(category_id = 32, user=request.user)
    remedical_subject = filtered_remedical.aggregate(Sum('credit'))['credit__sum']

    filtered_information = Subject.objects.filter(category_id = 10,  user=request.user)
    information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
    rest_infomation = 8 - (information_subject or 0)

    filterd_field = Subject.objects.filter(category_id = 6, user=request.user)
    field_subject = filterd_field.aggregate(Sum('credit'))['credit__sum']

    filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
    free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

    specialize_subject = (gakubu_subject or 0) + (department_subject or 0)+ (field_subject or 0) + (information_subject or 0) + (remedical_subject or 0)
    rest_specialize = 92 - (specialize_subject or 0)

    foreign_language = (first_language or 0) + (second_language or 0)
    rest_foreign = 20 - (foreign_language or 0)
    
    total_credit = (kyoutu or 0) + (first_language or 0) + (second_language or 0) + (gakubu_subject or 0) + (department_subject or 0) + (information_subject or 0) + (field_subject or 0) + (remedical_subject or 0) 
    #total_credit = all_credit - (free_subject or 0)

    # kyoutu = Subject.objects.filter(category_id = 4)
    rest_credit = 128 - (total_credit or 0 )
    return render(request, 'total.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'gakubu_subject': gakubu_subject, 
                                          'department_subject': department_subject, 'information_subject':information_subject, 'field_subject':field_subject, 'remedical_subject': remedical_subject,
                                          'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 
                                          'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_gakubu': rest_gakubu, 'rest_department': rest_department, 'rest_information': rest_infomation, 
                                          'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject})

"""
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
"""