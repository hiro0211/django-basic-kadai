from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Product
from django.urls import reverse_lazy
from django.views.generic import DetailView

class TopView(TemplateView):
    template_name = "top.html"

class ProductListView(ListView):
  model = Product
  paginate_by = 3
 
class ProductCreateView(CreateView):
  model = Product
  fields = '__all__'

class ProductUpadateView(UpdateView):
   model = Product
   fields = "__all__"
   template_name_suffix = "_update_form"

class ProductDeleteView(DeleteView):
   model = Product
   success_url = reverse_lazy("list")

class ProductDetailView(DetailView):
   model = Product
   context_object_name = 'Product'
   template_name = "product_detail.html"