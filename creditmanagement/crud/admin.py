from django.contrib import admin
from .models import Subject, Category

class SubjectAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'credit', 'score', 'category')
  search_fields = ('name',) 
  list_filter = ('category', )

class CategoryAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'requiredment_credit')
  search_fields = ('name',)

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Category, CategoryAdmin)