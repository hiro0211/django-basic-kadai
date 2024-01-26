from django.db import models
from django.urls import reverse 
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission

class Student(models.Model):
  grade = models.CharField(
    '学年', max_length=5, blank=False, null=True,
    choices=(('1年', '1年'),('2年', '2年'), 
              ('3年', '3年'),('4年', '4年')),
    default='4年'
  )
  semester = models.CharField(
    '現在の学期', max_length=5, blank=False, null=True,
    choices=(('前期', '前期'), ('後期', '後期')),
    default='後期'
  )
  faculty = models.CharField(
    '学部', max_length=10, blank=False, null=True,
    choices=(('経済学部', '経済学部'), ('経営学部', '経営学部'), 
            ('法学部', '法学部')),
    default='経済学科'
  )
  department = models.CharField(
    '学科', max_length=20, blank=False, null=True,
    choices=(('経済学科', '経済学科'), ('国際経済学科', '国際経済学科'), 
            ('総合経済政策学科', '総合経済政策学科'), ('経営学科', '経営学科'),
            ('商学科', '商学科'), ('会計学科', '会計学科'), 
            ('キャリアマネジメント学科', 'キャリアマネジメント学科')),
    default='経済学科'
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
  is_required = models.BooleanField(verbose_name="必修科目", default=False)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('list') 

"""
class Student(models.Model):
  name = models.CharField(max_length=100)
  subjects = models.ManyToManyField(Subject)
  """