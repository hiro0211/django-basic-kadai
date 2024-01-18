from django.db import models
from django.urls import reverse 
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission

class Student(models.Model):
  grade = models.CharField(
    '学年と学期', max_length=5, 
    choices=(('1年前期', '1年前期'),('1年後期', '1年後期'),('2年前期', '2年前期'), ('2年後期', '2年後期'),
              ('3年前期', '3年前期'), ('3年後期', '3年後期'), ('4年前期', '4年前期'), ('4年後期', '4年後期'))
  )
  department = models.CharField(
    '学科', max_length=5,
    choices=(('経済学部', '経済学部'), ('経営学部', '経営学部'), 
            ('法学部', '法学部')),
    default='経営学部'
  )
  user= models.OneToOneField(settings.AUTH_USER_MODEL, 
on_delete=models.CASCADE, blank=True, null=True)

class Category(models.Model):
  name = models.CharField(max_length=200, verbose_name="科目カテゴリ")
  requiredment_credit = models.PositiveIntegerField(default=0)
  
  def __str__(self):
    return self.name

class Subject(models.Model):
  name = models.CharField(max_length=100, verbose_name="科目名") 
  credit = models.FloatField(null=True, blank=False, verbose_name="単位数", default=2.0)
  score = models.PositiveIntegerField(verbose_name="得点", default=70)
  category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="科目カテゴリ")
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('list') 

"""
class Student(models.Model):
  name = models.CharField(max_length=100)
  subjects = models.ManyToManyField(Subject)
  """