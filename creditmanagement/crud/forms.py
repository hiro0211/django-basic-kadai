from typing import Any
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.fields import Field
from .models import Student
from django.forms import ModelForm
from django.db import models

class LoginForm(AuthenticationForm):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs["class"] = 'form-control'
      field.widget.attrs['placeholder'] = field.label

class SignUpForm(UserCreationForm):
  username = forms.EmailField(max_length=254, label="大学のメールアドレス")
  class Meta:
    model = User
    fields = ["username", "password1", "password2"]

class SignUpForm2(forms.ModelForm):
  class Meta:
    model = Student
    fields = ["grade", "faculty", "department", "semester"]
  
class StudentChangeForm(ModelForm):
  class Meta:
    model = Student
    fields = ["grade", "faculty", "department", "semester"]
  
  def __init__(self, grade=None, faculty=None, department=None, semester=None, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)

    if grade:
      self.fields['grade'].widget.attrs['value'] = grade
    if faculty:
      self.fields['faculty'].widget.attrs['value'] = faculty
    if department:  
      self.fields['department'].widget.attrs['value'] = department
    if semester:
      self.fields['semester'].widget.attrs['value'] = semester
  
  def update(self, student):
    student.grade = self.cleaned_data['grade']
    student.faculty = self.cleaned_data['faculty']
    student.department = self.cleaned_data['department']
    student.semester = self.cleaned_data['semester']
    student.save()
    
class SiteAuthDataForm(forms.Form):
  user_id = forms.CharField(label="UnipaユーザID")
  password = forms.CharField(label="Unipaパスワード", widget=forms.PasswordInput(), min_length=8)

class ConfirmDeleteForm(forms.Form):
  confirm_delete = forms.BooleanField(label= "本当に削除しても？", initial= False, required=False)