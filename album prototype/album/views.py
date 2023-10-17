from django.shortcuts import render
from django.views.generic import ListView,DetailView

from .models import Photo

class PhotoListView(ListView):
  model = Photo
  template_name = "album/photo_list.html"
  context_object_name = "photos"

class PhotoDetailView(DetailView):
  model = Photo 
  template_name = "album/photo_detail.html"
  context_object_name = "photo" 