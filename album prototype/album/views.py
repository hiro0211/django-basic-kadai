from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView,DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Tag, Photo

class PhotoListView(ListView):
  model = Photo
  template_name = "album/photo_list.html"
  context_object_name = "photos"

  def get_context_data(self, *args, **kwargs):
      context = super() .get_context_data(*args, **kwargs)
      context["tags"] = Tag.objects.all()
      return context 

class PhotoDetailView(DetailView):
  model = Photo 
  template_name = "album/photo_detail.html"
  context_object_name = "photo" 

class TagPhotoListView(ListView):
  model = Photo
  template_name = "album/tag_photo.html"
  context_object_name = "photos"

  def get_context_data(self, *args, **kwargs):
      context = super().get_context_data(*args, **kwargs)

      tag_name = self.kwargs["tag"]
      tag_name = get_object_or_404(Tag, name=tag_name)

      photos = Photo.objects.filter(tags=tag_name)
      
      context["tag"] = tag_name
      context["photos"] = photos

      return context
  
class PhotoCreateView(CreateView):
   model = Photo
   template_name = "album/photo_create.html"
   fields = "__all__"
   success_url = reverse_lazy("photo-list")

   def form_valid(self, form):
      photo = form.save()
      new_tag = self.request.POST.get("new_tag")

      if new_tag:
         print("追加前:", photo.tags.all())
         for tag in new_tag.split():
            is_exists = Tag.objects.filter(name=tag)
            if not is_exists:
               Tag.objects.create(name=tag)
            photo.tags.add(tag)
         print("追加後:", photo.tags.all())

      return redirect("photo-list")
   
class PhotoUpdateView(UpdateView):
   model = Photo
   fields = "__all__"
   template_name_suffix = "_update_form"
   success_url = reverse_lazy("photo-list")

class PhotoDeleteView(DeleteView):
   model = Photo
   success_url = reverse_lazy("photo-list")
   template_name = "album/photo_delete.html"