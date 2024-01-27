from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views import generic, View
from .models import Subject, Category, Student
from django.urls import reverse_lazy
from django.contrib.auth.views import (LoginView, LogoutView, PasswordContextMixin, PasswordChangeDoneView,
                                      PasswordChangeView, PasswordResetView, PasswordResetDoneView,
                                      PasswordResetConfirmView, PasswordResetCompleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import (SignUpForm, SiteAuthDataForm, LoginForm, SignUpForm2, 
                    StudentChangeForm, ConfirmDeleteForm) 
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
      subject_list = Subject.objects.filter(name__icontains=query, user=self.request.user)
    else:
      subject_list = Subject.objects.filter(user=self.request.user)
    return subject_list

class SubjectCreateView(LoginRequiredMixin, CreateView):
  model = Subject
  fields = '__all__'

def scrape_and_save_data(chrome_driver, semester_index, user, first_index=9):
    semester_elements = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[first_index + 2 * semester_index]  

    Subject.objects.filter(user=user).delete
    category = '' 
    for tr in semester_elements.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
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
              category_ = '第一外国語（英語）'
            else:
              category_ = '第二外国語'
          is_required = False
          if any(["基礎ゼミ" in kamoku, "演習Ⅰ" in kamoku, "演習Ⅱ" in kamoku]):
            is_required = True

            #print(category, kamoku)
          category_model , _ = Category.objects.get_or_create(name=category_)
          Subject.objects.create(category=category_model, name=kamoku, credit=credit, score=score, is_required=is_required, user=user)    
        
        else:
          category = kamoku

class LoadDataFromSite(generic.FormView):
    template_name= "crud/unipa_register.html"
    form_class = SiteAuthDataForm
    
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
        #ログインボタンをクリック
        button = chrome_driver.find_element(By.ID, 'form1:login')
        button.click()

        #chrome_driver.save_screenshot('screenshot.png')
        target_element = chrome_driver.find_element(By.ID, 'menuc3')
        actions = ActionChains(chrome_driver)
        actions.move_to_element(target_element).perform()

        grade = chrome_driver.find_element(By.ID, 'menuimg3-1')
        time.sleep(2)
        grade.click()

        #1年生後期の成績情報を取得
        user_grade = self.request.user.student.grade
        user_faculty = self.request.user.student.faculty
        user_semester = self.request.user.student.semester
        user_department = self.request.user.student.department

        #経済学部の処理を記述
        if all([user_grade == '1年', user_semester == "後期", user_faculty == "経済学部"]):
            for i in range(1):
              scrape_and_save_data(chrome_driver, i, self.request.user)
    
            return redirect("list")

        elif all([user_grade == '2年',user_semester == "前期", user_faculty == "経済学部"]):   
          for i in range(2):
            scrape_and_save_data(chrome_driver, i, self.request.user)
    
          return redirect("list")

        elif all([user_grade == '2年',user_semester == "後期", user_faculty == "経済学部"]):
          for i in range(3):
            scrape_and_save_data(chrome_driver, i, self.request.user)
    
          return redirect("list")

        elif all([user_grade == '3年', user_semester == "前期", user_faculty == "経済学部"]):
          for i in range(4):
            scrape_and_save_data(chrome_driver, i, self.request.user)
    
          return redirect("list")

        elif all([user_grade == '3年', user_semester == "前期", user_faculty == "経済学部"]):

          for i in range(5):
            scrape_and_save_data(chrome_driver, i, self.request.user)
          return redirect("list")

        elif all([user_grade == '4年', user_semester == "前期", user_faculty == "経済学部"]):

          for i in range(6):
            scrape_and_save_data(chrome_driver, i, self.request.user, first_index=10)    
          return redirect("list")

        elif all([user_grade == '4年', user_semester == "後期", user_faculty == "経済学部"]):
            
          for i in range(7):
            scrape_and_save_data(chrome_driver, i, self.request.user, first_index=10)
          return redirect("list")
        
        #経営学部の処理を記述
        elif all([user_grade == '2年', user_faculty == "経営学部"]):
            #成績情報を取得
            grade_element = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[39]

            Subject.objects.filter(user=self.request.user).delete
            category = '' 
            for tr in grade_element.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
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

        elif all([user_grade == '3年',  user_faculty == "経営学部"]):
            grade_element = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[39]

            Subject.objects.filter(user=self.request.user).delete
            category = '' 
            for tr in grade_element.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
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

        elif all([user_grade == '4年', user_faculty == "経営学部"]):

            #成績情報を取得
            grade_element = chrome_driver.find_elements(By.CSS_SELECTOR, 'table.outline>tbody>tr')[39]

            Subject.objects.filter(user=self.request.user).delete
            category = '' 
            for tr in grade_element.find_elements(By.CSS_SELECTOR, 'table>tbody>tr')[1:]:
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

  def post(self, request, *args, **kwargs):
    if 'confirm_delete' in request.POST:
      return super().post(request, *args, **kwargs)
    else:
      return redirect('list')

class SubjectDeleteAllView(View):
    template_name = 'crud/subject_confirm_delete_all.html'

    def get(self, request, *args, **kwargs):
        subjects = Subject.objects.filter(user=self.request.user)
        return render(request, self.template_name, {'subjects': subjects})
    
    def post(self, request, *args, **kwargs):
        if 'confirm_delete' in request.POST:
            Subject.objects.filter(user=self.request.user).delete()
            return redirect('list')
        else:
            # キャンセルボタンが押された場合の処理
            return redirect('list') 

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

def get_department_choices(request):
    faculty = request.GET.get('faculty')
    
    if faculty == "経済学部":
        department_choices = [
            ("経済学科", "経済学科"),
            ("国際経済学科", "国際経済学科"),
            ("総合経済政策学科", "総合経済政策学科")
        ]
    elif faculty == "経営学部":
        department_choices = [
            ("経営学科", "経営学科"),
            ("商学科", "商学科"),
            ("会計学科", "会計学科"),
            ("キャリアマネジメント学科", "キャリアマネジメント学科")
        ]
    else:
        department_choices = []

    return JsonResponse({'choices': department_choices})

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

class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
  template_name = 'crud/password_change_done.html'

class MyPasswordReset(PasswordResetView):
  subject_template_name = 'crud/mail_template/reset/subject.txt'
  email_template_name = 'crud/mail_template/reset/message.txt'
  template_name = 'crud/password_reset_form.html'
  success_url = reverse_lazy('password_reset_done')

class MyPasswordResetConfirm(PasswordResetCompleteView):
  success_url = reverse_lazy('password_reset_complete')
  template_name = 'crud/password_reset_confirm.html'

class MyPasswordResetDone(PasswordResetDoneView):
  template_name = 'crud/password_reset_done.html'

class MyPasswordResetComplete(PasswordResetCompleteView):
  template_name = 'crud/password_reset_complete.html'

class StudentProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'crud/student_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = get_object_or_404(Student, user=self.request.user)
        return context

class StudentChangeView(LoginRequiredMixin, FormView):
    template_name = 'crud/student_change.html'
    form_class = StudentChangeForm
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        student = get_object_or_404(Student, user=self.request.user)
        student.grade = form.cleaned_data['grade']
        student.semester = form.cleaned_data['semester']
        student.faculty = form.cleaned_data['faculty']
        student.department = form.cleaned_data['department']
        student.save()

        messages.success(self.request, 'プロフィールが更新されました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'プロフィールの更新に失敗しました。')
        return super().form_invalid(form)

def calculate_total(request):
    user_faculty = request.user.student.faculty
    user_grade = request.user.student.grade 
    required_list = []

    if all([user_faculty == "経済学部", user_grade == '1年']):
        #必修科目を入れる。
        
        required_list = ["基礎ゼミ", "演習Ⅰ", "演習Ⅱ"]
        filtered_required = Subject.objects.filter(is_required=True, user=request.user)
        filtered_required = [subject.name for subject in filtered_required]

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

        filtered_remedial = Subject.objects.filter(category_id = 32, user=request.user)
        remedial_subject = filtered_remedial.aggregate(Sum('credit'))['credit__sum']

        filtered_information = Subject.objects.filter(category_id = 10,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 8 - (information_subject or 0)

        filterd_field = Subject.objects.filter(category_id = 6, user=request.user)
        field_subject = filterd_field.aggregate(Sum('credit'))['credit__sum']

        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        specialize_subject = (gakubu_subject or 0) + (department_subject or 0)+ (field_subject or 0) + (information_subject or 0) + (remedial_subject or 0)
        rest_specialize = 92 - (specialize_subject or 0)

        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 20 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (first_language or 0) + (second_language or 0) + (gakubu_subject or 0) + (department_subject or 0) + (information_subject or 0) + (field_subject or 0) + (remedial_subject or 0) 
        #total_credit = all_credit - (free_subject or 0)

        #3年生への進級要件
        rest_promotion = 56 - (total_credit or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 128 - (total_credit or 0 )
        return render(request, 'economics_total.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'gakubu_subject': gakubu_subject, 
                                              'department_subject': department_subject, 'information_subject':information_subject, 'field_subject':field_subject, 'remedial_subject': remedial_subject,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_gakubu': rest_gakubu, 'rest_department': rest_department, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject, 'rest_promotion': rest_promotion, 
                                              'filtered_required': filtered_required, 'required_list': required_list})

    elif all([user_faculty == "経済学部", user_grade == '2年']):
        #必修科目を入れる。
        required_list = ["基礎ゼミ", "演習Ⅰ", "演習Ⅱ"]
        filtered_required = Subject.objects.filter(is_required=True, user=request.user)
        filtered_required = [subject.name for subject in filtered_required]

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

        filtered_remedial = Subject.objects.filter(category_id = 32, user=request.user)
        remedial_subject = filtered_remedial.aggregate(Sum('credit'))['credit__sum']

        filtered_information = Subject.objects.filter(category_id = 10,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 8 - (information_subject or 0)

        filterd_field = Subject.objects.filter(category_id = 6, user=request.user)
        field_subject = filterd_field.aggregate(Sum('credit'))['credit__sum']

        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        specialize_subject = (gakubu_subject or 0) + (department_subject or 0)+ (field_subject or 0) + (information_subject or 0) + (remedial_subject or 0)
        rest_specialize = 92 - (specialize_subject or 0)

        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 20 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (first_language or 0) + (second_language or 0) + (gakubu_subject or 0) + (department_subject or 0) + (information_subject or 0) + (field_subject or 0) + (remedial_subject or 0) 
        #total_credit = all_credit - (free_subject or 0)

        #3年生への進級要件
        rest_promotion = 56 - (total_credit or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 128 - (total_credit or 0 )
        return render(request, 'economics_total.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'gakubu_subject': gakubu_subject, 
                                              'department_subject': department_subject, 'information_subject':information_subject, 'field_subject':field_subject, 'remedial_subject': remedial_subject,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_gakubu': rest_gakubu, 'rest_department': rest_department, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject, 'rest_promotion': rest_promotion, 
                                              'filtered_required': filtered_required, 'required_list': required_list})

    elif all([user_faculty == "経済学部", user_grade == '3年']):
        required_list = ["基礎ゼミ", "演習Ⅰ", "演習Ⅱ"]
        filtered_required = Subject.objects.filter(is_required=True, user=request.user)
        filtered_required = [subject.name for subject in filtered_required]

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

        filtered_remedial = Subject.objects.filter(category_id = 32, user=request.user)
        remedial_subject = filtered_remedial.aggregate(Sum('credit'))['credit__sum']

        filtered_information = Subject.objects.filter(category_id = 10,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 8 - (information_subject or 0)

        filterd_field = Subject.objects.filter(category_id = 6, user=request.user)
        field_subject = filterd_field.aggregate(Sum('credit'))['credit__sum']

        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        specialize_subject = (gakubu_subject or 0) + (department_subject or 0)+ (field_subject or 0) + (information_subject or 0) + (remedial_subject or 0)
        rest_specialize = 92 - (specialize_subject or 0)

        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 20 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (first_language or 0) + (second_language or 0) + (gakubu_subject or 0) + (department_subject or 0) + (information_subject or 0) + (field_subject or 0) + (remedial_subject or 0) 
        #total_credit = all_credit - (free_subject or 0)

        #4年生への進級要件
        rest_promotion = 92 - (total_credit or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 128 - (total_credit or 0 )
        return render(request, 'economics_total.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'gakubu_subject': gakubu_subject, 
                                              'department_subject': department_subject, 'information_subject':information_subject, 'field_subject':field_subject, 'remedial_subject': remedial_subject,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_gakubu': rest_gakubu, 'rest_department': rest_department, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject, 'rest_promotion': rest_promotion, 'filtered_required': filtered_required,
                                              'required_list': required_list})

    elif all([user_faculty == "経済学部", user_grade == '4年']):
        #必修科目を入れる。
        required_list = ["基礎ゼミ", "演習Ⅰ", "演習Ⅱ"]
        filtered_required = Subject.objects.filter(is_required=True, user=request.user)
        filtered_required = [subject.name for subject in filtered_required]

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

        filtered_remedial = Subject.objects.filter(category_id = 32, user=request.user)
        remedial_subject = filtered_remedial.aggregate(Sum('credit'))['credit__sum']

        filtered_information = Subject.objects.filter(category_id = 10,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 8 - (information_subject or 0)

        filterd_field = Subject.objects.filter(category_id = 6, user=request.user)
        field_subject = filterd_field.aggregate(Sum('credit'))['credit__sum']

        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        specialize_subject = (gakubu_subject or 0) + (department_subject or 0)+ (field_subject or 0) + (information_subject or 0) + (remedial_subject or 0)
        rest_specialize = 92 - (specialize_subject or 0)

        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 20 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (first_language or 0) + (second_language or 0) + (gakubu_subject or 0) + (department_subject or 0) + (information_subject or 0) + (field_subject or 0) + (remedial_subject or 0) 

        rest_credit = 128 - (total_credit or 0 )
        return render(request, 'economics_total.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'gakubu_subject': gakubu_subject, 
                                              'department_subject': department_subject, 'information_subject':information_subject, 'field_subject':field_subject, 'remedial_subject': remedial_subject,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_gakubu': rest_gakubu, 'rest_department': rest_department, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject, 'filtered_required': filtered_required, 'required_list': required_list})

    elif all([user_faculty == "経営学部", user_grade == '1年']):
        filtered_kyoutu = Subject.objects.filter(category_id = 1, user=request.user)
        kyoutu = filtered_kyoutu.aggregate(Sum('credit'))['credit__sum']
        rest_kyoutu = 20 - (kyoutu or 0)

        filtered_first = Subject.objects.filter(category_id = 2, user=request.user)
        first_language = filtered_first.aggregate(Sum('credit'))['credit__sum']
        rest_fisrt = 14 - (first_language or 0)

        filtered_second = Subject.objects.filter(category_id = 3, user=request.user)
        second_language = filtered_second.aggregate(Sum('credit'))['credit__sum']
        rest_second = 2 - (second_language or 0)

        #基礎科目の処理
        filtered_basic = Subject.objects.filter(category_id = 7, user=request.user)
        basic_subject = filtered_basic.aggregate(Sum('credit'))['credit__sum']
        rest_basic = 14 - (basic_subject or 0)

        #基幹科目の処理
        filtered_core = Subject.objects.filter(category_id = 9, user=request.user)
        core_subject = filtered_core.aggregate(Sum('credit'))['credit__sum']
        rest_core = 32 - (core_subject or 0)

        #関連科目の処理
        filtered_relate = Subject.objects.filter(category_id = 11, user=request.user)
        relate_subject = filtered_relate.aggregate(Sum('credit'))['credit__sum']

        #情報科目の処理
        filtered_information = Subject.objects.filter(category_id = 8,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 10 - (information_subject or 0)

        #総合科目の処理
        filterd_comprehensive = Subject.objects.filter(category_id = 12, user=request.user)
        comprehensive_subject = filterd_comprehensive.aggregate(Sum('credit'))['credit__sum']
        rest_comprehensive = 8 - (comprehensive_subject or 0)
        
        #自由科目の処理
        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        #他コース科目の処理
        filtered_other_course = Subject.objects.filter(category_id = 13, user=request.user) 
        other_course = filtered_other_course.aggregate(Sum('credit'))['credit__sum']

        #他学科科目の処理
        filtered_other_subject = Subject.objects.filter(category_id = 14, user=request.user)
        other_subject = filtered_other_subject.aggregate(Sum('credit'))['credit__sum']

        #専門科目の処理
        specialize_subject = (basic_subject or 0) + (core_subject or 0)+ (comprehensive_subject or 0) + (information_subject or 0) + (relate_subject or 0) + (other_course or 0) + (other_subject or 0)
        rest_specialize = 86 - (specialize_subject or 0)

        #外国語科目の処理
        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 18 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (specialize_subject or 0) + (foreign_language or 0)
        #total_credit = all_credit - (free_subject or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 124 - (total_credit or 0 )
        return render(request, 'business_administration.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'basic_subject': basic_subject, 'other_course': other_course, 'ohter_subject': other_subject,
                                              'core_subject': core_subject, 'information_subject':information_subject, 'comprehensive_subject':comprehensive_subject, 'relate_subject': relate_subject, 'rest_core': rest_core,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 'rest_second': rest_second,
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_basic': rest_basic, 'rest_comprehensive': rest_comprehensive, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject})

    elif all([user_faculty == "経営学部", user_grade == '2年']):
        filtered_kyoutu = Subject.objects.filter(category_id = 1, user=request.user)
        kyoutu = filtered_kyoutu.aggregate(Sum('credit'))['credit__sum']
        rest_kyoutu = 20 - (kyoutu or 0)

        filtered_first = Subject.objects.filter(category_id = 2, user=request.user)
        first_language = filtered_first.aggregate(Sum('credit'))['credit__sum']
        rest_fisrt = 14 - (first_language or 0)

        filtered_second = Subject.objects.filter(category_id = 3, user=request.user)
        second_language = filtered_second.aggregate(Sum('credit'))['credit__sum']
        rest_second = 2 - (second_language or 0)

        #基礎科目の処理
        filtered_basic = Subject.objects.filter(category_id = 7, user=request.user)
        basic_subject = filtered_basic.aggregate(Sum('credit'))['credit__sum']
        rest_basic = 16 - (basic_subject or 0)

        #基幹科目の処理
        filtered_core = Subject.objects.filter(category_id = 9, user=request.user)
        core_subject = filtered_core.aggregate(Sum('credit'))['credit__sum']
        rest_core = 32 - (core_subject or 0)

        #関連科目の処理
        filtered_relate = Subject.objects.filter(category_id = 11, user=request.user)
        relate_subject = filtered_relate.aggregate(Sum('credit'))['credit__sum']

        #情報科目の処理
        filtered_information = Subject.objects.filter(category_id = 8,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 10 - (information_subject or 0)

        #総合科目の処理
        filterd_comprehensive = Subject.objects.filter(category_id = 12, user=request.user)
        comprehensive_subject = filterd_comprehensive.aggregate(Sum('credit'))['credit__sum']
        rest_comprehensive = 8 - (comprehensive_subject or 0)
        
        #自由科目の処理
        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        #他コース科目の処理
        filtered_other_course = Subject.objects.filter(category_id = 13, user=request.user) 
        other_course = filtered_other_course.aggregate(Sum('credit'))['credit__sum']

        #他学科科目の処理
        filtered_other_subject = Subject.objects.filter(category_id = 14, user=request.user)
        other_subject = filtered_other_subject.aggregate(Sum('credit'))['credit__sum']

        #専門科目の処理
        specialize_subject = (basic_subject or 0) + (core_subject or 0)+ (comprehensive_subject or 0) + (information_subject or 0) + (relate_subject or 0) + (other_course or 0) + (other_subject or 0)
        rest_specialize = 86 - (specialize_subject or 0)

        #外国語科目の処理
        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 18 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (specialize_subject or 0) + (foreign_language or 0)
        #total_credit = all_credit - (free_subject or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 124 - (total_credit or 0 )
        return render(request, 'business_administration.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'basic_subject': basic_subject, 'other_course': other_course, 'ohter_subject': other_subject,
                                              'core_subject': core_subject, 'information_subject':information_subject, 'comprehensive_subject':comprehensive_subject, 'relate_subject': relate_subject, 'rest_core': rest_core,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 'rest_second': rest_second,
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_basic': rest_basic, 'rest_comprehensive': rest_comprehensive, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject})

    elif all([user_faculty == "経営学部", user_grade == '3年']):
        filtered_kyoutu = Subject.objects.filter(category_id = 1, user=request.user)
        kyoutu = filtered_kyoutu.aggregate(Sum('credit'))['credit__sum']
        rest_kyoutu = 20 - (kyoutu or 0)

        filtered_first = Subject.objects.filter(category_id = 2, user=request.user)
        first_language = filtered_first.aggregate(Sum('credit'))['credit__sum']
        rest_fisrt = 14 - (first_language or 0)

        filtered_second = Subject.objects.filter(category_id = 3, user=request.user)
        second_language = filtered_second.aggregate(Sum('credit'))['credit__sum']
        rest_second = 2 - (second_language or 0)

        #基礎科目の処理
        filtered_basic = Subject.objects.filter(category_id = 7, user=request.user)
        basic_subject = filtered_basic.aggregate(Sum('credit'))['credit__sum']
        rest_basic = 14 - (basic_subject or 0)

        #基幹科目の処理
        filtered_core = Subject.objects.filter(category_id = 9, user=request.user)
        core_subject = filtered_core.aggregate(Sum('credit'))['credit__sum']
        rest_core = 32 - (core_subject or 0)

        #関連科目の処理
        filtered_relate = Subject.objects.filter(category_id = 11, user=request.user)
        relate_subject = filtered_relate.aggregate(Sum('credit'))['credit__sum']

        #情報科目の処理
        filtered_information = Subject.objects.filter(category_id = 8,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 10 - (information_subject or 0)

        #総合科目の処理
        filterd_comprehensive = Subject.objects.filter(category_id = 12, user=request.user)
        comprehensive_subject = filterd_comprehensive.aggregate(Sum('credit'))['credit__sum']
        rest_comprehensive = 8 - (comprehensive_subject or 0)
        
        #自由科目の処理
        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        #他コース科目の処理
        filtered_other_course = Subject.objects.filter(category_id = 13, user=request.user) 
        other_course = filtered_other_course.aggregate(Sum('credit'))['credit__sum']

        #他学科科目の処理
        filtered_other_subject = Subject.objects.filter(category_id = 14, user=request.user)
        other_subject = filtered_other_subject.aggregate(Sum('credit'))['credit__sum']

        #専門科目の処理
        specialize_subject = (basic_subject or 0) + (core_subject or 0)+ (comprehensive_subject or 0) + (information_subject or 0) + (relate_subject or 0) + (other_course or 0) + (other_subject or 0)
        rest_specialize = 86 - (specialize_subject or 0)

        #外国語科目の処理
        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 18 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (specialize_subject or 0) + (foreign_language or 0)
        #total_credit = all_credit - (free_subject or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 124 - (total_credit or 0 )
        return render(request, 'business_administration.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'basic_subject': basic_subject, 'other_course': other_course, 'ohter_subject': other_subject,
                                              'core_subject': core_subject, 'information_subject':information_subject, 'comprehensive_subject':comprehensive_subject, 'relate_subject': relate_subject, 'rest_core': rest_core,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 'rest_second': rest_second,
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_basic': rest_basic, 'rest_comprehensive': rest_comprehensive, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject})

    elif all([user_faculty == "経営学部", user_grade == '4年']):
        filtered_kyoutu = Subject.objects.filter(category_id = 1, user=request.user)
        kyoutu = filtered_kyoutu.aggregate(Sum('credit'))['credit__sum']
        rest_kyoutu = 20 - (kyoutu or 0)

        filtered_first = Subject.objects.filter(category_id = 2, user=request.user)
        first_language = filtered_first.aggregate(Sum('credit'))['credit__sum']
        rest_fisrt = 14 - (first_language or 0)

        filtered_second = Subject.objects.filter(category_id = 3, user=request.user)
        second_language = filtered_second.aggregate(Sum('credit'))['credit__sum']
        rest_second = 2 - (second_language or 0)

        #基礎科目の処理
        filtered_basic = Subject.objects.filter(category_id = 7, user=request.user)
        basic_subject = filtered_basic.aggregate(Sum('credit'))['credit__sum']
        rest_basic = 14 - (basic_subject or 0)

        #基幹科目の処理
        filtered_core = Subject.objects.filter(category_id = 9, user=request.user)
        core_subject = filtered_core.aggregate(Sum('credit'))['credit__sum']
        rest_core = 32 - (core_subject or 0)

        #関連科目の処理
        filtered_relate = Subject.objects.filter(category_id = 11, user=request.user)
        relate_subject = filtered_relate.aggregate(Sum('credit'))['credit__sum']

        #情報科目の処理
        filtered_information = Subject.objects.filter(category_id = 8,  user=request.user)
        information_subject = filtered_information.aggregate(Sum('credit'))['credit__sum']
        rest_infomation = 10 - (information_subject or 0)

        #総合科目の処理
        filterd_comprehensive = Subject.objects.filter(category_id = 12, user=request.user)
        comprehensive_subject = filterd_comprehensive.aggregate(Sum('credit'))['credit__sum']
        rest_comprehensive = 8 - (comprehensive_subject or 0)
        
        #自由科目の処理
        filtered_free = Subject.objects.filter(category_id = 31, user=request.user)
        free_subject = filtered_free.aggregate(Sum('credit'))['credit__sum']

        #他コース科目の処理
        filtered_other_course = Subject.objects.filter(category_id = 13, user=request.user) 
        other_course = filtered_other_course.aggregate(Sum('credit'))['credit__sum']

        #他学科科目の処理
        filtered_other_subject = Subject.objects.filter(category_id = 14, user=request.user)
        other_subject = filtered_other_subject.aggregate(Sum('credit'))['credit__sum']

        #専門科目の処理
        specialize_subject = (basic_subject or 0) + (core_subject or 0)+ (comprehensive_subject or 0) + (information_subject or 0) + (relate_subject or 0) + (other_course or 0) + (other_subject or 0)
        rest_specialize = 86 - (specialize_subject or 0)

        #外国語科目の処理
        foreign_language = (first_language or 0) + (second_language or 0)
        rest_foreign = 18 - (foreign_language or 0)
        
        total_credit = (kyoutu or 0) + (specialize_subject or 0) + (foreign_language or 0)
        #total_credit = all_credit - (free_subject or 0)

        # kyoutu = Subject.objects.filter(category_id = 4)
        rest_credit = 124 - (total_credit or 0 )
        return render(request, 'business_administration.html', {'kyoutu':kyoutu, 'first_language': first_language, 'second_language': second_language, 'basic_subject': basic_subject, 'other_course': other_course, 'ohter_subject': other_subject,
                                              'core_subject': core_subject, 'information_subject':information_subject, 'comprehensive_subject':comprehensive_subject, 'relate_subject': relate_subject, 'rest_core': rest_core,
                                              'specialize_subject':specialize_subject, 'foreign_language': foreign_language, 'total_credit': total_credit, 'rest_credit': rest_credit, 'rest_second': rest_second,
                                              'rest_kyoutu': rest_kyoutu, 'rest_first': rest_fisrt, 'rest_basic': rest_basic, 'rest_comprehensive': rest_comprehensive, 'rest_information': rest_infomation, 
                                              'rest_specialize': rest_specialize, 'rest_foreign': rest_foreign, 'free_subject': free_subject})